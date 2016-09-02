function(doc) {

    //tender checks
    var startDate = (doc.enquiryPeriod || {}).startDate;
    if ( (!startDate) || (startDate < "2016-04-01") ) {return;}
    if (doc.procurementMethod !== "open") {return;}
    if ((doc.mode || "") === "test") { return;}

    var bids_disclojure_date = (doc.qualificationPeriod || {}).startDate || (doc.awardPeriod || {}).startDate || null;
    if (!bids_disclojure_date) {return;}

    //global tender values
    var kind = doc.procuringEntity.kind || "_kind";
    var owner = doc.owner;
    var tender_id = doc._id;
    var tender_status = doc.status;
    var tenderID = doc.tenderID;
    var datemodified = doc.dateModified;



    var count_lot_bids = function(lot, bids) {
        return ( bids || [] ).map(function(bid) {
            return ( bid.lotValues || [] ).filter(function(value) {
                return value.relatedLot === lot.id;
            }).length;
        }).reduce(function( total, curr) {
            return total + curr;
        }, 0) || 0;
    };


    var count_lot_qualifications = function(qualifications, lot_id) {
        if ( (typeof qualifications === 'undefined') || (qualifications.length === 0) ) {
            return 0;
        }
        return qualifications.filter(function(qualification) {
            return qualification.lotID === lot_id;
        }).length;
    }



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
        return ((typeof date === 'object') ? date : (new Date(date))).toISOString().slice(0, 23);
    };


    var find_complaint_date = function(complaints) {
        return new Date(Math.max.apply(null, complaints.map(function(c) {
            var d = (c.type === 'claim') ? c.dateAnswered : c.dateDecision;
            if ( (typeof d === 'undefined') || (d === null) ) {
                return null;
            } else {
                return new Date(d);
            }
        }).filter(function(d) {
            return d !== null; 
        })));

    };

    var find_cancellation_max_date = function(cancellations) {
        if ((typeof cancellations === 'undefined') || (cancellations.length === 0)) {
            return null;
        }
        if (cancellations.length > 1) {
            return max_date(tender_cancellations.reduce(function(prev_doc, curr_doc) {
                return ( prev_doc.date > curr_doc.date ) ? curr_doc : prev_doc;
            }));
        } else {
            return max_date(cancellations[0]);
        }
    };

    var find_awards_max_date = function(awards) {
        if ((typeof awards === 'undefined') || (awards.length === 0)) {
            return null;
        }
        var date = new Date(Math.max.apply(null, awards.map(function(aw) {
            if('complaints' in aw)  {
                var d = find_complaint_date(aw.complaints);
                if (isNaN(d.getTime())) {
                    return new Date(aw.complaintPeriod.endDate);
                } else {
                    return d;
                }
            } else {
                return new Date(aw.complaintPeriod.endDate);
            }
        })));
        return  date;
    };

    var Handler = function (tender){
        this.status = tender.status;
        this.is_multilot = ( "lots" in tender ) ? true:false; 
        this.bids_disclosure_standstill = new Date(bids_disclojure_date);
        if ('date' in tender) {
            if (['complete', 'cancelled', 'unsuccessful'].indexOf(tender.status) !== -1) {
                if (tender.status === 'cancelled') {
                    if ((new Date(tender.date)) < this.bids_disclosure_standstill) {
                        this.tender_date = null;
                    } else {
                        this.tender_date = new Date(tender.date);
                    }
                } else {
                    this.tender_date = new Date(tender.date);
                }
            } else {
                this.tender_date = null;
            }
        } else {
            switch (this.status) {
            case 'complete':
                this.tender_date = new Date( Math.max.apply(null, ( tender.contracts || [] ).filter(function(c) {
                    return c.status === 'active';
                }).map(function(c){
                    return max_date(c);
                })));
                break;
            case 'unsuccessful':
                this.tender_date = find_awards_max_date(tender.awards);
                break;
            case 'cancelled':
                var cancellation_date = find_cancellation_max_date(tender.cancellations.filter(function(cancellation) {
                    return ( (cancellation.status === 'active') && (cancellation.cancellationOf === 'tender') );
                }));
                if (cancellation_date < this.bids_disclosure_standstill) {
                    this.tender_date = null;
                } else {
                    this.tender_date = cancellation_date;
                }
                break;
            default:
                this.tender_date = null;
            } }
    };

    var lotHandler = function (lot, tender){
        this.status = lot.status;
        this.tender_handler = new Handler(tender);
        if ('date' in lot) {
            if (['complete', 'cancelled', 'unsuccessful'].indexOf(lot.status) !== -1) {
                if (this.status === 'cancelled') {
                    if ((new Date(lot.date)) < this.tender_handler.bids_disclosure_standstill) {
                        this.lot_date = null;
                    } else {
                        this.lot_date = new Date(lot.date);
                    }
                } else {
                    this.lot_date = new Date(lot.date);
                }
            } else {
                if (this.tender_handler.status === 'cancelled') {
                    this.lot_date = (this.tender_handler.tender_date !== null) ? this.tender_handler.tender_date : null;
                } else {
                    this.lot_date = null;
                }
            }
        } else { 
            switch(this.status) {
            case 'unsuccessful':
                this.lot_date = find_awards_max_date(( tender.awards || [] ).filter(function(award) {
                    return award.lotID === lot.id;
                }));
                break;
            case 'cancelled':
                var lot_cancellation = find_cancellation_max_date(tender.cancellations.filter(function(cancellation) {
                    return (cancellation.status === 'active') && (cancellation.cancellationOf === 'lot') && (cancellation.relatedLot === lot.id);
                }));
                if ((lot_cancellation !== null) && (lot_cancellation > this.tender_handler.bids_disclosure_standstill)) {
                    this.lot_date = lot_cancellation;
                } else {
                    this.lot_date = null;
                }
                 break;
            case 'complete':

                var contract_date = '';
                tender.awards.forEach(function(award) {
                    if (award.lotID === lot.id) {
                        (tender.contracts || []).forEach(function(contract) {
                            if (award.id === contract.awardID) {
                                if (contract.status === 'active') {
                                   contract_date = max_date(contract);
                                }
                            }
                        });
                    }
                });
                this.lot_date = contract_date || null;
                break;
            default:
            if (tender.status === 'cancelled') {
                    if (this.tender_handler.tender_date !== null) {
                        if ( this.tender_handler.tender_date > this.tender_handler.bids_disclosure_standstill) {
                            this.lot_date = this.tender_handler.tender_date;
                        }
                    } else {
                        this.lot_date = null;
                    }
                } else {
                    var lotDate = '';
                    ( tender.awards || [] ).forEach(function(award) {
                        if (award.lotID === lot.id) {
                            (tender.contracts || []).forEach(function(contract) {
                                if (award.id === contract.awardID) {
                                    if (contract.status === 'active') {
                                        lotDate = max_date(contract);
                                    }
                                }
                            });
                        }
                    });
                    this.lot_date = lotDate || null;
                }
        } }
    }; // lotHandle

    var emitter = {
        lot: function(lot, date) {
            emit([owner, date_normalize(date), lot.id], {
                tender: tender_id,
                lot: lot.id,
                value: lot.value.amount,
                currency: lot.value.currency,
                kind: kind,
                lot_status: lot.status,
                status: tender_status,
                datemodified: datemodified,
                startdate: startDate,
                tenderID: tenderID,
            });
        },
        tender: function(tender,date) {
            emit([owner, date_normalize(date)], {
                tender: tender_id,
                value: tender.value.amount,
                currency: tender.value.currency,
                kind: kind,
                status: tender_status,
                datemodified: datemodified,
                startdate: startDate,
                tenderID: tenderID,
            });
        }
    };

    var check_lot = function(lot, tender) {

        if ( tender.procurementMethodType === 'aboveThresholdUA' ) {
            if (count_lot_bids(lot, tender.bids) > 1) {
                return true; 
            }
        } else if (tender.procurementMethodType === 'aboveThresholdEU') {
            if (count_lot_qualifications(tender.qualifications, lot.id) > 1) {
                return true; 
            }

        } else if (tender.procurementMethodType === 'aboveThresholdUA.defense') {
            var lot_awards = ('awards' in tender) ? (
                tender.awards.filter(function(a) {
                    return a.lotID === lot.id;
                })
            ) : [];
            if ( ( (count_lot_bids(lot, tender.bids) < 2 ) && (lot_awards.length === 0))) {
                return false;
            } else {
                return true;
            }
        } else {
            if (count_lot_bids(lot, tender.bids) > 0) {
                return true; 
            }
        }
        return false;
    };

    var check_tender = function(tender) {
        if ( tender.procurementMethodType === 'aboveThresholdUA' ) {
            if (tender.numberOfBids > 1) {
                return true;
            }
        } else if (tender.procurementMethodType === 'aboveThresholdEU') {
            if ( ( tender.qualifications.length || []) > 1) { 
                return true;
            }

        } else if (tender.procurementMethodType === 'aboveThresholdUA.defense') {
            if( (tender.numberOfBids < 2) && !('awards' in tender)) {
                log('skip tender '+tender.id + " bids: "+ tender.numberOfBids);
                return false;
            } else {
                return true;
            }
        } else {
            if (tender.numberOfBids > 0) {
                return true;
            }
        }
        return false;
    };


    var find_tender_data = function(tender) {
        var handler = new Handler(tender);
        if (handler.is_multilot) {
            tender.lots.forEach(function(lot){
                if ( check_lot(lot, tender) ) {
                    var lot_handler = new lotHandler(lot, tender);
                    if (lot_handler.lot_date !== null) {
                        emitter.lot(lot, lot_handler.lot_date);
                    }
                }
            });

        } else {

            if (check_tender(tender)) {
                if (tender.status === 'cancelled') {
                    if (handler.tender_date < handler.bids_disclosure_standstill) { return; }
                }
                if (handler.tender_date !==  null) {
                    emitter.tender(tender, handler.tender_date);
                }
            }
        }
    };

    find_tender_data(doc);
}// end function

