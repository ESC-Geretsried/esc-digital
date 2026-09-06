(function () {
  if (!window.wp || !wp.blocks || !wp.element) return;
  wp.blocks.registerBlockType('esc-river-rats/community', {
    edit: function () {
      return wp.element.createElement('div', { className: 'esc-community-editor-placeholder' }, 'Gemeinschaft (wird automatisch ausgegeben)');
    },
    save: function () { return null; }
  });
}());
