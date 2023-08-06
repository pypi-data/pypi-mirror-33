

(function(globals) {

  var django = globals.django || (globals.django = {});

  
  django.pluralidx = function(n) {
    var v=n != 1;
    if (typeof(v) == 'boolean') {
      return v ? 1 : 0;
    } else {
      return v;
    }
  };
  

  /* gettext library */

  django.catalog = django.catalog || {};
  
  var newcatalog = {
    "(one more date)": [
      "\u00e9\u00e9n andere datum",
      "andere datums"
    ],
    "All": "Alle",
    "An error has occurred.": "Er is een fout opgetreden.",
    "An error of type {code} occurred.": "Er is een fout opgetreden met code {code}.",
    "Barcode area": "Barcode gebied",
    "Cart expired": "Winkelwagen is verlopen",
    "Check-in QR": "QR-code voor check-in",
    "Close message": "Sluit bericht",
    "Comment:": "Opmerking:",
    "Contacting Stripe \u2026": "Verbinding maken met Stripe \u2026",
    "Copied!": "Gekopieerd!",
    "Count": "Aantal",
    "Do you really want to leave the editor without saving your changes?": "Wilt u de editor verlaten zonder uw wijzigingen op te slaan?",
    "Error while uploading your PDF file, please try again.": "Probleem bij het uploaden van het PDF bestand, probeer opnieuw.",
    "Generating messages \u2026": "Bezig met het genereren van berichten \u2026",
    "Group of objects": "Groep van objecten",
    "Lead Scan QR": "QR-code voor lead-scanning",
    "Marked as paid": "Gemarkeerd als betaald",
    "None": "Geen",
    "Object": "Object",
    "Others": "Andere",
    "Paid orders": "Betaalde bestellingen",
    "Placed orders": "Gemaakte bestellingen",
    "Press Ctrl-C to copy!": "Gebruik Ctrl-C om te kopi\u00ebren!",
    "Saving failed.": "Opslaan mislukt.",
    "Text object": "Tekstobject",
    "The PDF background file could not be loaded for the following reason:": "Het PDF achtergrondbestand kon niet geladen worden met als reden:",
    "The items in your cart are no longer reserved for you.": "De items in uw winkelwagen zijn niet meer voor u gereserveerd.",
    "The items in your cart are reserved for you for one minute.": [
      "De items in uw winkelwagen zijn voor u gereserveerd voor \u00e9\u00e9n minuut.",
      "De items in uw winkelwagen zijn voor u gereserveerd voor {num} minuten."
    ],
    "The request took to long. Please try again.": "De aanvraag duurde te lang, probeer alstublieft opnieuw.",
    "Ticket design": "Ticketontwerp",
    "Total revenue": "Volledige omzet",
    "Unknown error.": "Onbekende fout.",
    "Use a different name internally": "Gebruik intern een andere naam",
    "We are currently sending your request to the server. If this takes longer than one minute, please check your internet connection and then reload this page and try again.": "Uw aanvraag wordt naar de server verstuurd. Als dit langer dan een minuut duurt, controleer uw internetverbinding en probeer opnieuw.",
    "We are processing your request \u2026": "Uw aanvraag is in behandeling \u2026",
    "We currently cannot reach the server, but we keep trying. Last error code: {code}": "De server is op dit moment niet bereikbaar, we proberen opnieuw. Laatste foutcode: {code}",
    "We currently cannot reach the server. Please try again. Error code: {code}": "De server is op dit moment niet bereikbaar, probeer alstublieft opnieuw. Foutcode: {code}",
    "Your request has been queued on the server and will now be processed. Depending on the size of your event, this might take up to a few minutes.": "Uw aanvraag is in behandeling op de server. Afhankelijk van de grootte van het evenement kan dit enkele minuten duren.",
    "Your request has been queued on the server and will now be processed. If this takes longer than two minutes, please contact us or go back in your browser and try again.": "Uw aanvraag wordt in behandeling genomen op de server. Als dit langer dan twee minuten duurt, neem contact met ons op of probeer opnieuw.",
    "widget\u0004<a href=\"https://pretix.eu\" target=\"_blank\" rel=\"noopener\">event ticketing powered by pretix</a>": "<a href=\"https://pretix.eu\" target=\"_blank\" rel=\"noopener\">ticketsysteem mogelijk gemaakt door pretix</a>",
    "widget\u0004Buy": "Kopen",
    "widget\u0004Close": "Sluiten",
    "widget\u0004Close ticket shop": "Sluit ticketverkoop",
    "widget\u0004Continue": "Verdergaan",
    "widget\u0004FREE": "GRATIS",
    "widget\u0004Only available with a voucher": "Alleen beschikbaar met een voucher",
    "widget\u0004Redeem": "Verzilveren",
    "widget\u0004Redeem a voucher": "Verzilver een voucher",
    "widget\u0004Reserved": "Gereserveerd",
    "widget\u0004See variations": "Zie variaties",
    "widget\u0004Sold out": "Uitverkocht",
    "widget\u0004The cart could not be created. Please try again later": "De winkelwagen kon niet gemaakt worden. Probeer alstublieft later opnieuw",
    "widget\u0004The ticket shop could not be loaded.": "De ticketverkoop kon niet geladen worden.",
    "widget\u0004Voucher code": "Vouchercode",
    "widget\u0004Waiting list": "Wachtlijst",
    "widget\u0004You currently have an active cart for this event. If you select more products, they will be added to your existing cart. Click on this message to continue checkout with your cart.": "U heeft momenteel een actieve winkelwagen voor dit evenement. Als u meer producten selecteert worden deze toegevoegd aan uw bestaande winkelwagen. Klik op dit bericht om verder te gaan met uw winkelwagen.",
    "widget\u0004currently available: %s": "momenteel beschikbaar: %s",
    "widget\u0004from %(currency)s %(price)s": "vanaf %(currency)s %(price)s",
    "widget\u0004incl. %(rate)s% %(taxname)s": "incl. %(rate)s% %(taxname)s",
    "widget\u0004minimum amount to order: %s": "minimale hoeveelheid om te bestellen: %s",
    "widget\u0004plus %(rate)s% %(taxname)s": "plus %(rate)s% %(taxname)s"
  };
  for (var key in newcatalog) {
    django.catalog[key] = newcatalog[key];
  }
  

  if (!django.jsi18n_initialized) {
    django.gettext = function(msgid) {
      var value = django.catalog[msgid];
      if (typeof(value) == 'undefined') {
        return msgid;
      } else {
        return (typeof(value) == 'string') ? value : value[0];
      }
    };

    django.ngettext = function(singular, plural, count) {
      var value = django.catalog[singular];
      if (typeof(value) == 'undefined') {
        return (count == 1) ? singular : plural;
      } else {
        return value[django.pluralidx(count)];
      }
    };

    django.gettext_noop = function(msgid) { return msgid; };

    django.pgettext = function(context, msgid) {
      var value = django.gettext(context + '\x04' + msgid);
      if (value.indexOf('\x04') != -1) {
        value = msgid;
      }
      return value;
    };

    django.npgettext = function(context, singular, plural, count) {
      var value = django.ngettext(context + '\x04' + singular, context + '\x04' + plural, count);
      if (value.indexOf('\x04') != -1) {
        value = django.ngettext(singular, plural, count);
      }
      return value;
    };

    django.interpolate = function(fmt, obj, named) {
      if (named) {
        return fmt.replace(/%\(\w+\)s/g, function(match){return String(obj[match.slice(2,-2)])});
      } else {
        return fmt.replace(/%s/g, function(match){return String(obj.shift())});
      }
    };


    /* formatting library */

    django.formats = {
    "DATETIME_FORMAT": "j F Y H:i",
    "DATETIME_INPUT_FORMATS": [
      "%d-%m-%Y %H:%M:%S",
      "%d-%m-%y %H:%M:%S",
      "%Y-%m-%d %H:%M:%S",
      "%d/%m/%Y %H:%M:%S",
      "%d/%m/%y %H:%M:%S",
      "%Y/%m/%d %H:%M:%S",
      "%d-%m-%Y %H:%M:%S.%f",
      "%d-%m-%y %H:%M:%S.%f",
      "%Y-%m-%d %H:%M:%S.%f",
      "%d/%m/%Y %H:%M:%S.%f",
      "%d/%m/%y %H:%M:%S.%f",
      "%Y/%m/%d %H:%M:%S.%f",
      "%d-%m-%Y %H.%M:%S",
      "%d-%m-%y %H.%M:%S",
      "%d/%m/%Y %H.%M:%S",
      "%d/%m/%y %H.%M:%S",
      "%d-%m-%Y %H.%M:%S.%f",
      "%d-%m-%y %H.%M:%S.%f",
      "%d/%m/%Y %H.%M:%S.%f",
      "%d/%m/%y %H.%M:%S.%f",
      "%d-%m-%Y %H:%M",
      "%d-%m-%y %H:%M",
      "%Y-%m-%d %H:%M",
      "%d/%m/%Y %H:%M",
      "%d/%m/%y %H:%M",
      "%Y/%m/%d %H:%M",
      "%d-%m-%Y %H.%M",
      "%d-%m-%y %H.%M",
      "%d/%m/%Y %H.%M",
      "%d/%m/%y %H.%M",
      "%d-%m-%Y",
      "%d-%m-%y",
      "%Y-%m-%d",
      "%d/%m/%Y",
      "%d/%m/%y",
      "%Y/%m/%d"
    ],
    "DATE_FORMAT": "j F Y",
    "DATE_INPUT_FORMATS": [
      "%d-%m-%Y",
      "%d-%m-%y",
      "%d/%m/%Y",
      "%d/%m/%y",
      "%Y-%m-%d"
    ],
    "DECIMAL_SEPARATOR": ",",
    "FIRST_DAY_OF_WEEK": "1",
    "MONTH_DAY_FORMAT": "j F",
    "NUMBER_GROUPING": "3",
    "SHORT_DATETIME_FORMAT": "j-n-Y H:i",
    "SHORT_DATE_FORMAT": "j-n-Y",
    "THOUSAND_SEPARATOR": ".",
    "TIME_FORMAT": "H:i",
    "TIME_INPUT_FORMATS": [
      "%H:%M:%S",
      "%H:%M:%S.%f",
      "%H.%M:%S",
      "%H.%M:%S.%f",
      "%H.%M",
      "%H:%M"
    ],
    "YEAR_MONTH_FORMAT": "F Y"
  };

    django.get_format = function(format_type) {
      var value = django.formats[format_type];
      if (typeof(value) == 'undefined') {
        return format_type;
      } else {
        return value;
      }
    };

    /* add to global namespace */
    globals.pluralidx = django.pluralidx;
    globals.gettext = django.gettext;
    globals.ngettext = django.ngettext;
    globals.gettext_noop = django.gettext_noop;
    globals.pgettext = django.pgettext;
    globals.npgettext = django.npgettext;
    globals.interpolate = django.interpolate;
    globals.get_format = django.get_format;

    django.jsi18n_initialized = true;
  }

}(this));

