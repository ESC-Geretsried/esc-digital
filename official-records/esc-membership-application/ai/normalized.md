# ESC Membership Application — AI-normalized record

Record ID: `esc-membership-application`
Class: `form`
Status: `APPROVED CURRENT TEMPLATE` with one known superseded operational note
Source date printed on form: 2018-04-19, V18
Authority confirmation: Founder, 2026-08-23
Official source: https://www.esc-geretsried.de/static/225f3452b00217a764bf6ef83b3b57fe/ESC-River-Rats-Beitrittserklrung-v19.pdf

## Purpose

Official ESC membership application and change-notification template. This file is a derived machine-readable representation, not the original legal/administrative source artifact.

## Structured field model

Primary member fields:
- surname, given name, date of birth;
- department selection: Eishockey, Eiskunstlauf, Inklusionssport, Cheerleader;
- telephone, fax, mobile, email;
- street/house number, postal code, city.

Family membership:
- up to four additional family members on the current source form;
- each family member has surname, given name, date of birth and optional department selection;
- if no separate department is selected for a family member, the primary selection applies according to the source form.

Membership attributes:
- individual membership;
- family membership;
- trial membership;
- active or passive status;
- reduced-contribution evidence categories shown on the current form: education/training, unemployed, pensioner, person with disability.

Required declarations/sections:
- acknowledgement of Satzung and applicable organizational/contribution rules;
- signature of member or legal guardian;
- additional guardian declaration for minors;
- SEPA recurring direct-debit mandate;
- member-data/privacy declaration;
- optional communication consent for email/telephone;
- image/publication consent section.

SEPA reference data:
- creditor identifier on the approved form: `DE30ZZZ00001270905`;
- mandate reference is assigned separately;
- account-holder name/contact/address, bank, BIC, IBAN, place/date/signature are captured.

## Current submission process

The source form contains an old operational statement that only original-paper submissions are accepted and email/fax is not accepted. That statement is superseded by the current Satzung.

Current governing rule for admission processing: a fully completed and signed written admission application may be submitted to the Geschäftsstelle by letter or by email. Therefore future UI/process models must not reproduce the old no-email rule as current authority.

## AI usage rules

- Use this record for field/schema derivation.
- Use `esc-satzung` and `esc-geschaeftsordnung` for current process/rule interpretation where they conflict with old operational wording on this form.
- Never claim that generating a PDF or filling an online assistant submits the application unless the configured delivery mechanism actually performs that submission.
- Never persist submitted member data in this official-record package.
