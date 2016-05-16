function(doc) {
  var data = doc;
  var id = data._id;
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
  var emit_results = function(tender) {

    var odate = (tender.qualificationPeriod || {}).startDate || (tender.awardPeriod || {}).startDate || null;
    if (!odate) {
        return;
    }
    var date = (new Date(odate)).toISOString().slice(0, 23);
    var startDate = (doc.enquiryPeriod||{}).startDate;
    if ((tender.procurementMethod === "open") && (tender.mode !== "test")) {
      if (("bids" in tender) && ("lots" in tender)) {
        var audits = [];
        tender.lots.forEach(function(lot) {
          var lot_id = lot.id;
          (tender.documents || []).forEach(function(d) {
            if (d.title.indexOf("audit_" + id + "_" + lot_id) === 0) {
              if (audits.length > 0) {
                if (audits[0].dateModified > d.dateModified) {
                  audits.pop();
                  audits.push(d)
                }
              } else {
                audits.push(d);
              }
            }
          });
          var bids_filtered = filter_bids(tender.bids);
          var bids = find_bid_by_lot(bids_filtered, lot_id);
          for (var bid_id in bids) {
            var bid = bids[bid_id]
            var owner = bid.owner;
            emit([owner, date, bid.id, lot_id], {
              tender: id,
              lot: lot_id,
              value: lot.value.amount,
              currency: lot.value.currency,
              bid: bid.id,
              startdate: startDate,
              audits: audits[0],
              tender_start_date: tender.tenderPeriod.startDate,
              tenderID: tender.tenderID,
            })
          }
        });
      } else if ("bids" in tender) {
        var bids = filter_bids(tender.bids);
        var re = /audit/;
        var audits = [];
        (tender.documents || []).forEach(function(d) {
          if (d.title.match(re)) {
            if (audits.length > 0) {
              if (audits[0].dateModified > d.dateModified) {
                audits.pop();
                audits.push(d)
              }
            } else {
              audits.push(d);

            }
          }
        });
        bids.forEach(function(bid) {
          var owner = bid.owner;
          emit([owner, date, bid.id], {
            tender: id,
            value: tender.value.amount,
            currency: tender.value.currency,
            bid: bid.id,
            audits: audits[0],
            startdate: startDate,
            tender_start_date: tender.tenderPeriod.startDate,
            tenderID: tender.tenderID,
          })
        });
      };
    }
  }
  emit_results(data);
}
