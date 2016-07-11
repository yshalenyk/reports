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

    var date_normalize = function(date) {
        //return date in UTC format
        var ddate = '';
        if (typeof date !== 'object') {
            ddate = new Date(date)
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
            })
        });
        return results;
    }

    var filter_bids = function(bids) {
        var res = [];
        var min_date =  Date.parse("2016-04-01T00:00:00+03:00");
        bids.forEach(function(bid) {
            var bid_date =  Date.parse(bid.date);
            if ((["invalid", "deleted"].indexOf(bid.status || "active") === -1) && (+bid_date > +min_date)) {
                res.push(bid);
            }
        });
        return res;
    }

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
                tenderID: tenderID,
            });
        },
        tender: function(owner, date, bid, tender, audits){
            emit([owner, date, bid.id], {
                tender: tender.id,
                value: tender.value.amount,
                currency: tender.value.currency,
                bid: bid.id,
                audits: audits,
                startdate: startDate,
                tender_start_date: tender_start_date,
                tenderID: tenderID,
            }) 
        }
    }

    var emit_results = function(tender) {

        if ("bids" in tender) {
            var bids = filter_bids(tender.bids);
            if(is_multilot) {
                ( bids || [] ).forEach(function(bid) {
                    bid.lotValues.forEach(function(value) {
                        tender.lots.forEach(function(lot) {

                            if (value.relatedLot === lot.id) {
                                var audits = (  tender.documents || [] ).filter(function(tender_doc) {
                                    return tender_doc.title.indexOf("audit_" + id + "_" + lot.id) === 0;
                                });
                                var audit = '';
                                if ( audits.length > 0 ) {
                                    audit = audits.reduce(function(prev_doc, curr_doc) {
                                        return (prev_doc.dateModified > curr_doc.dateModified) ? curr_doc : prev_doc; 
                                    });
                                }
                                log(audit);

                                emitter.lot(bid.owner, date_normalize(bids_disclojure_date), bid, lot, audits[0]);
                            }
                        })
                    });
                });

            } else {
                var audits = (tender.documents || []).filter(function(tender_doc) {
                    return tender_doc.title.match(/audit/);
                })[0];
                ( bids || [] ).forEach(function(bid) {
                    emitter.tender(bid.owner, date_normalize(bids_disclojure_date), bid, tender, audits);
                });
            };

        }
    }

    emit_results(doc);
}
