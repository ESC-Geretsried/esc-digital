'use strict';

const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { GERETSRIED_TIME_ZONE, geretsriedDayIndex, dailyImageFor } = require('../src/static/js/hero-rotation.js');

const root = path.resolve(__dirname, '../..');
const heroes = JSON.parse(fs.readFileSync(path.join(root, 'content/home/heroes.json'), 'utf8'));
const homepage = fs.readFileSync(path.join(root, 'site/src/layouts/index.html'), 'utf8');
const youth = heroes.slides.find((slide) => slide.id === 'nachwuchs');

assert.equal(GERETSRIED_TIME_ZONE, 'Europe/Berlin');
assert.equal(geretsriedDayIndex(new Date('2026-03-28T22:30:00Z')), geretsriedDayIndex(new Date('2026-03-28T23:00:00Z')) - 1);
assert.equal(geretsriedDayIndex(new Date('2026-10-24T21:30:00Z')), geretsriedDayIndex(new Date('2026-10-24T22:30:00Z')) - 1);
assert.equal(dailyImageFor(['a', 'b'], new Date('2026-03-28T22:30:00Z')), dailyImageFor(['a', 'b'], new Date('2026-03-28T23:00:00Z')) === 'a' ? 'b' : 'a');

assert.deepEqual(youth.daily_images, [
  'images/teams/u7-team.jpg',
  'images/teams/u9-team.jpg',
  'images/teams/u13-team.jpg',
  'images/teams/u15-team.jpg',
  'images/teams/u17-team.jpg',
  'images/teams/u20-team.jpg'
]);
assert.ok(!youth.daily_images.some((image) => image.includes('u11')));
for (const image of youth.daily_images) assert.ok(fs.existsSync(path.join(root, image)), `missing approved youth image: ${image}`);

assert.equal(heroes.slides.length, 6);
assert.deepEqual(heroes.slides.map((slide) => slide.order), [10, 20, 30, 40, 50, 60]);
assert.ok(!homepage.includes('Nächstes Spiel'));
assert.ok(!homepage.includes('Aktuelles Spiel'));
assert.ok(homepage.includes('data-daily-images'));

console.log('Homepage hero structure and Europe/Berlin youth rotation validated');
