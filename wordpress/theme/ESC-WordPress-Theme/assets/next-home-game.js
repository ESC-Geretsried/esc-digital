(function () {
  'use strict';
  var cards = document.querySelectorAll('[data-next-home-game]');
  if (!cards.length) return;
  var now = new Date();
  var homePattern = /river\s*rats|rrg|geretsried/i;
  var datePattern = /(\d{1,2})[./-](\d{1,2})[./-](\d{4})/;
  var timePattern = /(\d{1,2}):(\d{2})/;
  function clean(value) { return (value || '').replace(/\s+/g, ' ').trim(); }
  function extractDateTime(text) {
    var match = clean(text).match(datePattern), time = clean(text).match(timePattern);
    if (!match) return null;
    var date = new Date(Number(match[3]), Number(match[2]) - 1, Number(match[1]));
    if (isNaN(date.getTime())) return null;
    if (time) date.setHours(Number(time[1]), Number(time[2]), 0, 0);
    return { date: date, dateLabel: String(date.getDate()).padStart(2, '0') + '.' + String(date.getMonth() + 1).padStart(2, '0') + '.' + date.getFullYear(), timeLabel: time ? String(time[1]).padStart(2, '0') + ':' + time[2] : '' };
  }
  function imageIn(cell) { var img = cell && cell.querySelector('img'); return img ? img.currentSrc || img.src : ''; }
  function names(cells) { return cells.map(function (cell) { return clean(cell.textContent); }).filter(function (value) { return value && value.length > 2 && !datePattern.test(value) && !timePattern.test(value) && !/^[-:–—+\d\s]+$/.test(value); }); }
  function hockeydata(doc) {
    var found = [];
    doc.querySelectorAll('.esc-gamepitch-widget table tbody tr').forEach(function (row) {
      var cells = Array.from(row.querySelectorAll('td')), dt = extractDateTime(row.textContent);
      if (!dt || dt.date < now || cells.length < 4) return;
      var teamNames = names(cells), homeIndex = teamNames.findIndex(function (value) { return homePattern.test(value); });
      if (homeIndex < 0) return;
      var home = teamNames[homeIndex], away = teamNames.find(function (value, index) { return index !== homeIndex; }) || 'Gegner';
      var homeCell = cells.find(function (cell) { return clean(cell.textContent) === home; }), awayCell = cells.find(function (cell) { return clean(cell.textContent) === away; });
      found.push({ date: dt.date, dateLabel: dt.dateLabel, timeLabel: dt.timeLabel, away: away, awayLogo: imageIn(awayCell), venue: 'Eisstadion Geretsried', source: 'Hockeydata' });
    });
    return found;
  }
  function sharepoint(doc) {
    var found = [];
    doc.querySelectorAll('.msgraph_calendar__table tbody tr').forEach(function (row) {
      var cells = Array.from(row.querySelectorAll('td')), raw = clean(row.textContent), dt = extractDateTime(raw);
      if (!dt || dt.date < now || !homePattern.test(raw)) return;
      var subject = cells.map(function (cell) { return clean(cell.textContent); }).find(function (value) { return /river\s*rats|rrg/i.test(value) && value.length > 8; }) || raw;
      var match = subject.match(/(?:river\s*rats|rrg)\s+vs\s+(.+)/i);
      if (!match) return;
      var venue = clean(cells[cells.length - 1] && cells[cells.length - 1].textContent) || raw;
      if (!/geretsried/i.test(venue)) return;
      found.push({ date: dt.date, dateLabel: dt.dateLabel, timeLabel: dt.timeLabel, away: clean(match[1]), venue: venue, source: 'Vorbereitungsspiele' });
    });
    return found;
  }
  function fetchDocument(url) {
    return new Promise(function (resolve, reject) {
      var frame = document.createElement('iframe');
      frame.src = url;
      frame.title = 'Spielplan-Daten';
      frame.setAttribute('aria-hidden', 'true');
      frame.style.cssText = 'position:absolute;width:1px;height:1px;border:0;opacity:0;pointer-events:none;';
      frame.onload = function () {
        window.setTimeout(function () {
          try { var doc = frame.contentDocument; if (!doc) throw new Error('schedule'); resolve(doc); } catch (error) { reject(error); }
          frame.remove();
        }, 1400);
      };
      frame.onerror = reject;
      document.body.appendChild(frame);
    });
  }
  function render(game) {
    cards.forEach(function (card) {
      var content = card.querySelector('.next-home-game__content');
      card.querySelector('[data-game-date]').textContent = game.dateLabel;
      card.querySelector('[data-game-time]').textContent = game.timeLabel || 'Spielzeit folgt';
      card.querySelector('[data-away-name]').textContent = game.away;
      card.querySelector('[data-game-venue]').textContent = game.venue;
      if (game.awayLogo) { var logo = card.querySelector('[data-away-logo]'); logo.src = game.awayLogo; logo.alt = game.away; logo.hidden = false; }
      card.querySelector('.next-home-game__loading').hidden = true;
      content.hidden = false;
    });
  }
  function showError() { cards.forEach(function (card) { card.querySelector('.next-home-game__loading').hidden = true; card.querySelector('.next-home-game__error').hidden = false; }); }
  Promise.allSettled([fetchDocument('/river-rats/'), fetchDocument('/vorbereitungsspiele-der-river-rats/')]).then(function (results) {
    var games = [];
    results.forEach(function (result) { if (result.status === 'fulfilled') games = games.concat(hockeydata(result.value), sharepoint(result.value)); });
    games.sort(function (a, b) { return a.date - b.date; });
    if (games[0]) render(games[0]); else showError();
  }).catch(showError);
}());
