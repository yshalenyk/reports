function(doc) {
    var startDate = (doc.enquiryPeriod||{}).startDate;
    if ( (startDate== null) || (startDate < "2016-04-01")) {
        return;
    }
    if (!(doc.procurementMethod === "open")) {
        return;
    }
    if ('mode' in doc) {
        if (doc.mode === 'test') {
            return;
        }
    }

    var find_kind = function(tender) {
        var kind = tender.procuringEntity.kind || '_kind';
        return kind;
    }

    var max_date = function(contract) {
        var dates = [];

        if ('date' in contract) {
            dates.push(new Date(contract.date));
        }

        if ('dateSigned' in contract) {
            dates.push(new Date(contract.dateSigned));
        }
        if ('documents' in contract) {
            contract.documents.forEach(function(docm) {
                dates.push(new Date(docm.datePublished));
            });
        }
        var maxDate = new Date(Math.max.apply(null, dates));
        return maxDate.toISOString().slice(0, 23);
    }

    var emit_unsuccessful_tenders = function(tender) {

        var owner = tender.owner;
        var kind = find_kind(tender);
        var date = '';

        if ('lots' in tender) {
            if (tender.status === 'cancelled') {
                date = max_date(tender.cancellations[0]);
                tender.lots.forEach(function(lot){
                    emit([owner, date, lot.id], {
                        tender: tender._id,
                        lot: lot.id,
                        value: lot.value.amount,
                        currency: lot.value.currency,
                        kind: kind,
                        status: tender.status,
                        datemodified: tender.dateModified,
                        startdate: startDate,
                        tenderID: tender.tenderID,
                    });
                });
            } else {
                tender.lots.forEach(function(lot){
                    if (lot.status === 'cancelled') {
                        //find cancellation date
                        tender.cancellations.forEach(function(cancellation) {
                            if ((cancellation.cancellationOf === 'lot') && (cancellation.relatedLot === lot.id)) {
                                date = max_date(cancellation);
                                emit([owner, date, lot.id], {
                                    tender: tender._id,
                                    lot: lot.id,
                                    value: lot.value.amount,
                                    currency: lot.value.currency,
                                    kind: kind,
                                    status: tender.status,
                                    datemodified: tender.dateModified,
                                    startdate: startDate,
                                    tenderID: tender.tenderID,
                                });
                            }
                        });
                    } else {
                        if ('awards' in tender) {
                            //find date in award
                            tender.awards.forEach(function(award){
                                if (award.lotID === lot.id) {
                                    date = award.complaintPeriod.endDate;
                                    var return_date = (new Date(date)).toISOString().slice(0, 23);
                                    emit([owner, return_date, lot.id], {
                                        tender: tender._id,
                                        lot: lot.id,
                                        value: lot.value.amount,
                                        currency: lot.value.currency,
                                        kind: kind,
                                        status: tender.status,
                                        datemodified: tender.dateModified,
                                        startdate: startDate,
                                        tenderID: tender.tenderID,
                                    });
                                }
                            });
                        } else {
                            date = (new Date((tender.qualificationPeriod || {}).endDate || (tender.tenderPeriod || {}).endDate)).toISOString().slice(0, 23);
                            emit([owner, date, lot.id], {
                                tender: tender._id,
                                lot: lot.id,
                                value: lot.value.amount,
                                currency: lot.value.currency,
                                kind: kind,
                                status: tender.status,
                                datemodified: tender.dateModified,
                                startdate: startDate,
                                tenderID: tender.tenderID,
                            });
                        }
                    }
                });
            }
        } else {
            if (tender.status === 'cancelled') {
                date = max_date(tender.cancellations[0]);
                emit([owner, date], {
                    tender: tender._id,
                    value: tender.value.amount,
                    currency: tender.value.currency,
                    kind: kind,
                    status: tender.status,
                    datemodified: tender.dateModified,
                    startdate: startDate,
                    tenderID: tender.tenderID,
                });
            } else {
                date = (new Date((tender.qualificationPeriod || {}).endDate || (tender.tenderPeriod || {}).endDate)).toISOString().slice(0, 23);
                emit([owner, date], {
                    tender: tender._id,
                    value: tender.value.amount,
                    currency: tender.value.currency,
                    kind: kind,
                    status: tender.status,
                    datemodified: tender.dateModified,
                    startdate: startDate,
                    tenderID: tender.tenderID,
                });

            }
        }
    }


    var emit_contracted_tenders = function(tender) {
        var kind = find_kind(tender);
        var dateModified = tender.dateModified;
        var owner = tender.owner;

        (tender.contracts||[]).forEach(function(contract) {
            if (contract.status !== 'active') {
                return;
            }
            var date = max_date(contract);
            if ('lots' in tender) {
                var award_id = contract.awardID;
                var lot_id = '';
                var value = '';
                var currency = '';
                tender.awards.forEach(function(award) {
                    if (award.id === award_id) {
                        lot_id = award.lotID;
                    }
                });

                tender.lots.forEach(function(lot) {
                    if (lot.id === lot_id) {
                        value = lot.value.amount;
                        currency = lot.value.currency;
                    }
                });

                emit([owner, date], {
                    tender: tender._id,
                    lot: lot_id,
                    value: value,
                    currency: currency,
                    kind: kind,
                    status: tender.status,
                    datemodified: tender.dateModified,
                    startdate: startDate,
                    tenderID: tender.tenderID,
                });
            } else {
                emit([owner, date], {
                    tender: tender._id,
                    value: tender.value.amount,
                    currency: tender.value.currency,
                    kind: kind,
                    status: tender.status,
                    startdate: startDate,
                    datemodified: tender.dateModified,
                    tenderID: tender.tenderID,
                });
            }
        });
    }
    if (doc.status !== 'cancelled' && doc.status !== 'unsuccessful') {
        emit_contracted_tenders(doc);
    } else {
        emit_unsuccessful_tenders(doc);
    }
}
