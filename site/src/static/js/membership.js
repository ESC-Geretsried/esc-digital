(() => {
  const form = document.getElementById('membership-form');
  if (!form) return;
  const familySection = document.getElementById('family-section');
  const familyMembers = document.getElementById('family-members');
  const addFamily = document.getElementById('add-family');
  const printPanel = document.getElementById('membership-print');
  const summary = document.getElementById('print-summary');
  let familyCount = 0;

  const esc = (value) => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const values = (name) => [...form.querySelectorAll(`[name="${name}"]:checked`)].map(el => el.value);
  const value = (name) => form.elements[name]?.value || '';

  function syncFamilyVisibility() {
    const selected = form.querySelector('[name="membership_type"]:checked')?.value;
    familySection.hidden = selected !== 'Familienmitgliedschaft';
    if (selected === 'Familienmitgliedschaft' && familyCount === 0) addFamilyMember();
  }

  function addFamilyMember() {
    if (familyCount >= 4) return;
    familyCount += 1;
    const card = document.createElement('div');
    card.className = 'family-card';
    card.dataset.family = String(familyCount);
    card.innerHTML = `<div class="family-card__head"><strong>Familienmitglied ${familyCount + 1}</strong><button type="button" aria-label="Familienmitglied entfernen">Entfernen</button></div>
      <div class="form-grid three"><label>Vorname<input name="family_${familyCount}_first"></label><label>Nachname<input name="family_${familyCount}_last"></label><label>Geburtsdatum<input type="date" name="family_${familyCount}_birth"></label></div>
      <fieldset class="nested"><legend>Abteilung</legend><div class="check-grid"><label><input type="checkbox" name="family_${familyCount}_department" value="Eishockey"> Eishockey</label><label><input type="checkbox" name="family_${familyCount}_department" value="Eiskunstlauf"> Eiskunstlauf</label><label><input type="checkbox" name="family_${familyCount}_department" value="Inklusionssport"> Inklusionssport</label><label><input type="checkbox" name="family_${familyCount}_department" value="Cheerleader"> Cheerleader</label></div></fieldset>`;
    card.querySelector('button').addEventListener('click', () => card.remove());
    familyMembers.append(card);
  }

  function row(label, val) {
    return val ? `<tr><td>${esc(label)}</td><td>${esc(val)}</td></tr>` : '';
  }

  function buildSummary() {
    const departments = values('department').join(', ');
    const discounts = values('discount').join(', ');
    let familyHtml = '';
    [...familyMembers.querySelectorAll('.family-card')].forEach(card => {
      const n = card.dataset.family;
      const first = value(`family_${n}_first`), last = value(`family_${n}_last`), birth = value(`family_${n}_birth`);
      const deps = [...form.querySelectorAll(`[name="family_${n}_department"]:checked`)].map(el => el.value).join(', ');
      if (first || last || birth) familyHtml += `<tr><td>Familienmitglied</td><td>${esc(`${first} ${last}`.trim())}${birth ? ` · ${esc(birth)}` : ''}${deps ? ` · ${esc(deps)}` : ''}</td></tr>`;
    });
    const comm = form.elements.communication_consent.checked ? 'Ja' : 'Nein';
    const photo = form.elements.photo_consent.checked ? 'Ja' : 'Nein';
    summary.innerHTML = `<section class="print-section"><h3>Mitgliedschaft</h3><table class="print-table">${row('Art', value('membership_type'))}${row('Status', value('status'))}${row('Mitglied', `${value('first_name')} ${value('last_name')}`.trim())}${row('Geburtsdatum', value('birth_date'))}${row('Abteilung', departments)}${familyHtml}${row('Ermäßigung/Nachweis', discounts)}</table></section>
      <section class="print-section"><h3>Kontakt</h3><table class="print-table">${row('E-Mail', value('email'))}${row('Telefon', value('phone'))}${row('Adresse', `${value('street')}, ${value('postal_code')} ${value('city')}`)}</table></section>
      <section class="print-section"><h3>SEPA-Lastschriftmandat</h3><table class="print-table">${row('Kontoinhaber', `${value('account_first_name')} ${value('account_last_name')}`.trim())}${row('IBAN', value('iban').replace(/\s+/g,'').toUpperCase())}${row('BIC', value('bic').toUpperCase())}${row('Kreditinstitut', value('bank_name'))}</table><p>Mandat für wiederkehrende Zahlungen: Ja. Gläubiger-ID DE30ZZZ00001270905.</p></section>
      <section class="print-section"><h3>Erklärungen</h3><table class="print-table">${row('Satzung/Geschäftsordnung', 'zur Kenntnis genommen')}${row('Datenschutzhinweise', 'zur Kenntnis genommen')}${row('Vereinskommunikation', comm)}${row('Bildverwendung', photo)}</table></section>`;
  }

  form.addEventListener('change', (event) => {
    if (event.target.name === 'membership_type') syncFamilyVisibility();
  });
  addFamily.addEventListener('click', addFamilyMember);

  form.addEventListener('submit', (event) => {
    event.preventDefault();
    if (!form.checkValidity()) {
      form.reportValidity();
      return;
    }
    buildSummary();
    printPanel.hidden = false;
    printPanel.scrollIntoView({behavior: 'smooth', block: 'start'});
    window.setTimeout(() => window.print(), 250);
  });
})();
