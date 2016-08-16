function(doc) {

    if (doc.procurementMethod !== "open") {return;}
    if ((doc.mode || "") === "test") { return;}

    var bids_disclojure_date = (doc.qualificationPeriod || {}).startDate || (doc.awardPeriod || {}).startDate || null;
    if(!bids_disclojure_date) { return; }

    var id = doc._id;
    var startDate = (doc.enquiryPeriod||{}).startDate;
    var tender_start_date = doc.tenderPeriod.startDate;
    var tenderID = doc.tenderID;
    var is_multilot = ( "lots" in doc )?true:false;

    var max_date = function (obj) {
        //helper function to find max date in object
        var dates = [];

        ['date', 'dateSigned', 'documents'].forEach(function(field){
            var date = obj[field] || '';
            if (date) {
                if (typeof date === "object") {
                    date.forEach(function(d) {
                        dates.push(new Date(d.datePublished));
                    });
                } else {
                    dates.push(new Date(date));
                }
            }
        });
        return new Date(Math.max.apply(null, dates));
    };

    var date_normalize = function(date) {
        //return date in UTC format
        var ddate = '';
        if (typeof date !== 'object') {
            ddate = new Date(date);
        } else {
            ddate = date;
        }
        return ddate.toISOString().slice(0, 23);
    };


    var find_bid_by_lot = function(bids, id) {
        results = [];
        bids.forEach(function(bid) {
            bid.lotValues.forEach(function(value) {
                if ((value.relatedLot === id) && ((["invalid"].indexOf(value.status || "active") === -1))) {
                    results.push(bid);
                }
            });
        });
        return results;
    };

    var filter_bids = function(bids) {
        var min_date =  Date.parse("2016-04-01T00:00:00+03:00");
        return bids.filter(function(bid) {
            var bid_date =  Date.parse(bid.date);
            return ((["invalid", "deleted"].indexOf(bid.status || "active") === -1) && (+bid_date > +min_date));
        });
    };

    var count_lot_bids = function(lot, bids) {
        return bids.map(function(bid) {
            return ( bid.lotValues || [] ).filter(function(value) {
                return value.relatedLot === lot.id;
            }).length;
        }).reduce(function( total, curr) {
            return total + curr;
        }, 0);
    };

    var check_tener = function(tender) {
        switch(tender.status) {
            case "cancelled":
                if ('date' in tender) {
                    if ((new Date( tender.date ) ) < ( new Date(bids_disclojure_date) )) {
                        return false;
                    }
                } else {
                    var tender_cancellations = ( tender.cancellations || [] ).filter(function(cancellation) {
                        return ( cancellation.status === 'active' ) && (cancellation.cancellationOf === 'tender');
                    });
                    if (tender_cancellations.length === 0) {
                        return false;
                    }
                    if (tender_cancellations.length > 1) {
                        cancel = tender_cancellations.reduce(function(prev_doc, curr_doc) {
                            return (max_date( prev_doc ) > max_date( curr_doc ))? curr_doc : prev_doc;
                        });

                        if (max_date( cancel ) < (new Date( bids_disclojure_date ))) {
                            return false;
                        }
                    } else {
                        if (max_date( tender_cancellations[0] ) < (new Date( bids_disclojure_date ))) {
                            return false;
                        }
                    }

                }
                return true;
            case "unsuccessful":
                if (['aboveThresholdUA', 'aboveThresholdEU'].indexOf(tender.procurementMethodType) !== -1) {
                    if (tender.numberOfBids < 2) {
                        return false;
                    }
                } else if (tender.procurementMethodType === 'aboveThresholdUA.defense') {
                    if( (tender.numberOfBids < 2) && !('awards' in tender)) {
                        return false;
                    }
                }
                return true;
            default:
                return true;
        }
    };

    var check_lot = function(tender, lot){
        switch (lot.status) {
            case "cancelled":
                if ('date' in lot) {
                    if ((new Date(lot.date)) < (new Date(bids_disclojure_date))) {
                        return false;
                    }

                } else {
                    lot_cancellation = ( tender.cancellations || []).filter(function(cancellation) {
                        if (( cancellation.status === 'active' ) && ( cancellation.cancellationOf === 'lot' ) && ( cancellation.relatedLot === lot.id )) {
                            return true;
                        }
                    });
                    if (lot_cancellation.length > 0) {
                        if (lot_cancellation.length > 1) {
                            cancel = lot_cancellation.reduce(function(prev_doc, curr_doc) {
                                return (max_date( prev_doc ) > max_date( curr_doc ))? curr_doc : prev_doc;
                            });

                            if (max_date( cancel ) < (new Date( bids_disclojure_date ))) {
                                return false;
                            }
                        } else {
                            if (max_date( lot_cancellation[0] ) < (new Date( bids_disclojure_date ))) {
                                return false;
                            }
                        }

                    }
                }

                return true;
            case "unsuccessful":
                if (['aboveThresholdUA', 'aboveThresholdEU'].indexOf(tender.procurementMethodType) !== -1) {
                    if (count_lot_bids(lot, tender.bids) < 2) {
                        return false;
                    }
                } else if (tender.procurementMethodType === 'aboveThresholdUA.defense') {
                    var lot_awards = ('awards' in tender) ? (
                        tender.awards.filter(function(a) {
                            return a.lotID === lot.id;
                        })
                    ) : [];
                    if ( ( (count_lot_bids(lot, tender.bids) < 2 ) && (lot_awards.length === 0))) {
                        return false;
                    }
                }
                return true;
            default:
                return true;
        }
    };

    var emitter = {
        lot: function(owner, date, bid, lot, audits) {
            emit([owner, date, bid.id, lot.id], {
                tender: id,
                lot: lot.id,
                value: lot.value.amount,
                currency: lot.value.currency,
                bid: bid.id,
                startdate: startDate,
                audits: audits,
                tender_start_date: tender_start_date,
                tenderID: tenderID
            });
        },
        tender: function(owner, date, bid, tender, audits){
            emit([owner, date, bid.id], {
                tender: id,
                value: tender.value.amount,
                currency: tender.value.currency,
                bid: bid.id,
                audits: audits,
                startdate: startDate,
                tender_start_date: tender_start_date,
                tenderID: tenderID
            });
        }
    };

    var emit_results = function(tender) {

        if ("bids" in tender) {
            var bids = filter_bids(tender.bids);
            if(is_multilot) {
                ( bids || [] ).forEach(function(bid) {
                    bid.lotValues.forEach(function(value) {
                        tender.lots.forEach(function(lot) {
                            if (check_lot(tender, lot)) {
                                if (value.relatedLot === lot.id) {
                                    var audits = (  tender.documents || [] ).filter(function(tender_doc) {
                                        return tender_doc.title.indexOf("audit_" + id + "_" + lot.id) === 0;
                                    });
                                    var audit = '';
                                    if ( audits.length > 1 ) {
                                        audit = audits.reduce(function(prev_doc, curr_doc) {
                                            return (prev_doc.dateModified > curr_doc.dateModified) ? curr_doc : prev_doc; 
                                        });
                                    } else {
                                        audit = audits[0] || null; 
                                    }
                                    emitter.lot(bid.owner, date_normalize(bids_disclojure_date), bid, lot, audit);
                                }
                            }

                        });
                    });
                });

            } else {
                if (!(check_tener(tender))) { return; }
                var audits = (tender.documents || []).filter(function(tender_doc) {
                    return tender_doc.title.match(/audit/);
                });
                var audit = '';
                if ( audits.length > 1 ) {
                    audit = audits.reduce(function(prev_doc, curr_doc) {
                        return (prev_doc.dateModified > curr_doc.dateModified) ? curr_doc : prev_doc; 
                    });
                } else {
                    audit = audits[0] || null; 
                }
                ( bids || [] ).forEach(function(bid) {
                    emitter.tender(bid.owner, date_normalize(bids_disclojure_date), bid, tender, audit);
                });
            }

        }
    };

    emit_results(doc);
}
