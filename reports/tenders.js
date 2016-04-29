function(doc) {
	
	var startDate = new Date(doc.enquiryPeriod.startDate);
	
	if (startDate < (new Date("2016-04-01T00:00+0300"))){
		return;
	}
	
	if (!(doc.procurementMethod==="open") ){
		return;
	}

	if ('mode' in doc) {
		if (doc.mode === 'test') {
			return;
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
            contract.documents.forEach(function (docm) {
                dates.push(new Date(docm.datePublished));
            });
        }
        var maxDate=new Date(Math.max.apply(null,dates));
        return mxDate.toISOString();
    }


	
    var emit_result = function (data) {


        var entity =  data.procuringEntity;
        if ('kind' in entity) {
             var kind = entity.kind;
        } else {
             var kind = '_kind';
        }

        var dateModified = data.dateModified;

		var owner = data.owner;

        data.contracts.forEach(function (contract) {
            if (contract.state === 'signed') {
				return;
			}
			var date = max_date(data.contract);
			if ('lots' in data) {
				var award_id = contract.awardID;
				
				data.awards.forEach(function (award) {
					if (award.id === award_id) {
						var lot_id = award.lotID;
					}
				});

				data.lots.forEach(function(lot) {
					if (lot.id  === lot_id) {
						var value = lot.value.amount;
					}
				});

				var result = {
					tender: data._id,
					lot: lot_id,
					value: value,
					kind: kind,
					datemodified: data.datemodified,
				}
				emit([owner, date], result);
			} else {
				var result = {
					tender: data._id,
					value: data.value,
					kind: kind,
					datemodified: data.datemodified,
				}
				emit([owner, date], result);

            }
			
		});
     }

	emit_result(doc);
}
