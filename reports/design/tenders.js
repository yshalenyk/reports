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
        var ddate = '';
        if (typeof date !== 'object') {
            ddate = new Date(date)
        } else {
            ddate = date;
        }
        return ddate.toISOString().slice(0, 23);
    };
    //*****************************************************************************************************************


    var Handler = function (tender){
        this.is_multilot = ( "lots" in tender )?true:false; 
        this.bids_disclosure_standstill = (tender.qualificationPeriod || {}).endDate || (tender.tenderPeriod || {}).endDate;
        this.last_complaint_standstill = ('awards' in tender)?tender.awards[tender.awards.length - 1].complaintPeriod.endDate:null;
        var tender_cancellation_date = '';
        if (tender.status === "cancelled" ) {
            var _cancellation_date ='';
            var c = tender.cancellations.map(function(cancellation) {
                if (( cancellation.status === 'active' ) && (cancellation.cancellationOf === 'tender')) {
                    _cancellation_date = max_date(cancellation);
                }
            });
            this.tender_cancellation_date = _cancellation_date;
        }

        if (tender.status === 'unsuccessful') {
            this.tender_unsuccessful_date = new Date(this.last_complaint_standstill || this.bids_disclosure_standstill);
        }
    }

    var lotHandler = function (lot, tender){
        this.status = lot.status;
        this.tender_handler = new Handler(tender);
        
        switch(this.status) {
            case 'unsuccessful':
                var lot_unsuccessful = '';
                if ('awards' in tender) {
                    tender.awards.forEach(function(award) {
                        if (award.lotID === lot.id) {
                            if (!(lot_unsuccessful) || (lot_unsuccessful < award.complaintPeriod.endDate)) {
                                lot_unsuccessful = award.complaintPeriod.endDate;
                            }
                        }
                    });
                } 
                this.lot_date = new Date( lot_unsuccessful || this.tender_handler.bids_disclosure_standstill );
                break;
            case 'cancelled':
                var lot_cancelled = '';
                tender.cancellations.forEach(function(cancellation) {
                    if (( cancellation.cancellationOf === 'lot' ) && (cancellation.status === 'active') && (cancellation.relatedLot === lot.id)) {
                        lot_cancelled = max_date(cancellation);
                    }
                })
                if ( !( lot_cancelled < (new Date(this.tender_handler.bids_disclosure_standstill)))) {
                    this.lot_date = lot_cancelled;
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
                this.lot_date = contract_date;
                break;
            default:
                if (tender.status === 'cancelled') {
                    if (!( this.tender_handler.tender_cancellation_date < (new Date(this.tender_handler.bids_disclosure_standstill)) )) {
                        this.lot_date = this.tender_handler.tender_cancellation_date;
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
                    this.lot_date = lotDate;
                }
        }
    } // lotHandler

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
    }


    var find_tender_data = function(tender) {
        var handler = new Handler(tender);
        switch(tender.status) {
            case 'cancelled':
                if (handler.is_multilot) {
                    tender.lots.forEach(function(lot){
                        var lot_handler = new lotHandler(lot, tender);
                        if (lot_handler.lot_date) {
                            emitter.lot(lot, lot_handler.lot_date);
                        }
                    });

                } else {

                    if (handler.tender_cancellation_date < (new Date(handler.bids_disclosure_standstill))) { return; }
                    emitter.tender(tender, handler.tender_cancellation_date);
                }
                break;
            case 'unsuccessful':
                if (handler.is_multilot) {
                    tender.lots.forEach(function(lot) {
                        var lot_handler = new lotHandler(lot, tender);
                        if (lot_handler.lot_date) {
                            emitter.lot(lot, lot_handler.lot_date);
                        }

                    });
                } else {
                    emitter.tender(tender, handler.tender_unsuccessful_date);
                }
                break;
            default:
                if (handler.is_multilot) {
                    tender.lots.forEach(function(lot) {
                       var lot_handler = new lotHandler(lot, tender);
                       if (lot_handler.lot_date) {
                           emitter.lot(lot, lot_handler.lot_date);
                       }
                    }); // forEach end
                } else {
                    ( tender.contracts || []).forEach(function(contract) {
                        if (contract.status === 'active') {
                            var date = max_date(contract);
                            emitter.tender(tender, date_normalize(date));
                        }
                    });
                }
        }
    }

    find_tender_data(doc);
}// end function

