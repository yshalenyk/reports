
function(doc) {

    //tender checks
    var startDate = (doc.enquiryPeriod || {}).startDate;
    if ( (!startDate) || (startDate < "2016-04-01") ) {return;}
    if (doc.procurementMethod !== "open") {return;}
    if ((doc.mode || "") === "test") { return;}

    //global tender values
    var kind = doc.procuringEntity.kind || "_kind";
    var owner = doc.owner;
    var tender_id = doc._id;
    var tender_status = doc.status;
    var tenderID = doc.tenderID;
    var datemodified = doc.dateModified;

    //*****************************************************************************************************************
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
    //*****************************************************************************************************************

    var date_normalize = function(date) {
        //return date in UTC format
        return date.toISOString().slice(0, 23);
    };
    //*****************************************************************************************************************

    var find_tender_unsuccessful_date = function(tender) {
        if ('awards' in tender) {
            var date = new Date(Math.max.apply(null, tender.awards.map(function(award) { return new Date(award.complaintPeriod.endDate); })));
        } else {
            var date = (new Date((tender.qualificationPeriod || {}).endDate || (tender.tenderPeriod || {}).endDate));
        }
        return date_normalize(date);
    }
    //*****************************************************************************************************************

    var find_lot_unsuccessful_date = function(lot_id, tender) {
        var date = '';
        if ('awards' in tender) {
            var lotDate = '';
            tender.awards.forEach(function(award) {
                if (award.lotID === lot_id) {
                    if (!(lotDate) || (lotDate < award.complaintPeriod.endDate)) {
                        lotDate = award.complaintPeriod.endDate;
                    }
                }
            });
            date = new Date(lotDate);
        } else {
            date = (new Date((tender.qualificationPeriod || {}).endDate || (tender.tenderPeriod || {}).endDate));

        }
        if (!date) {
            return find_tender_unsuccessful_date(tender);

        }
        return date_normalize(date);
    }
    //*****************************************************************************************************************

    var find_lot_cancellation_date = function(lot_id, tender) {
        var dates = [];
        tender.cancellations.forEach(function(cancellation) {
            if (( cancellation.cancellationOf === 'lot' ) && (cancellation.relatedLot === lot_id) && (cancellation.status === 'active')) {
                dates.push(max_date(cancellation));
            }
        });
        if (dates.length === 0) {
            return find_tender_cancellation_date(tender);
        }

        return date_normalize(new Date( Math.min.apply(null, dates) ));
    }
    //*****************************************************************************************************************



    var find_tender_cancellation_date = function(tender) {
        var dates = [];
        ( tender.cancellations || [] ).forEach(function(cancellation) {
            if (( cancellation.status === 'active' ) && ( cancellation.cancellationOf === 'tender' )) {
                dates.push(max_date(cancellation));
            }
        });
        return date_normalize(new Date(Math.min.apply(null, dates)));
    }
    //*****************************************************************************************************************

    var emit_lot_data = function(lot, date) {
        //helper for emit lot values by giving date
        emit([owner, date, lot.id], {
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

    }
    //*****************************************************************************************************************

    var emit_tender_data = function(tender, date) {
        //helper for emit tender data with given date
        emit([owner, date], {
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
    //*****************************************************************************************************************
    var find_tender_data = function(tender) {
        //main entry

        if ("lots" in tender) {
            tender.lots.forEach(function(lot) {
                if(lot.status === 'cancelled') {
                    if ('date' in lot) {
                        var date = date_normalize(new Date(lot.date) );
                    } else {
                        var date = find_lot_cancellation_date(lot.id, tender);
                    }
                    emit_lot_data(lot, date);

                } else if (lot.status === 'unsuccessful') {
                    if ('date' in lot) {
                        var date = date_normalize(new Date(lot.date));
                    } else {
                        var date = find_lot_unsuccessful_date(lot.id, tender);
                    }
                    emit_lot_data(lot, date);
                } else {
                    if (tender_status === 'cancelled') {
                        if ('date' in tender) {
                            var date = date_normalize(new Date(tender.date));
                        } else {
                            var date = find_tender_cancellation_date(tender);
                        }
                        emit_lot_data(lot, date);
                    } else {
                        ( tender.awards || []).forEach(function(award) {
                            if (award.lotID === lot.id) {
                                (tender.contracts || []).forEach(function(contract) {
                                    if (award.id === contract.awardID) {
                                        if (contract.status === 'active') {
                                            var date = date_normalize(max_date(contract));
                                            emit_lot_data(lot, date)
                                        }
                                    }
                                });
                            }
                        });
                 }
                }});
                } else {
                    if (tender.status === "unsuccessful" ) {
                        if ('date' in tender) {
                            var date = date_normalize(new Date(tender.date));
                        } else {
                            var date = find_tender_unsuccessful_date(tender);
                        }
                        emit_tender_data(tender, date);
                    } else if (tender.status === "cancelled") {
                        if ('date' in tender) {
                            var date = date_normalize(new Date(tender.date));
                        } else {
                            var date = find_tender_cancellation_date(tender);
                        }
                        emit_tender_data(tender, date);
                    } else {
                        ( tender.contracts || []).forEach(function(contract) {
                            if (contract.status === 'active') {
                                var date = max_date(contract);
                                emit_tender_data(tender, date_normalize( date ));
                            }
                        });
                    }
                }
            } // emit_tender_data
   

    find_tender_data(doc);
}

