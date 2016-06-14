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
        var entity = tender.procuringEntity;
        if ('kind' in entity) {
            var kind = entity.kind;
        } else {
            var kind = '_kind';
        }
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
    var emit_result = function(tender) {
        
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
                    startdate: startDate,
                    datemodified: tender.dateModified,
                    tenderID: tender.tenderID,
                });
            }
        });
    }

    emit_result(doc);
}
