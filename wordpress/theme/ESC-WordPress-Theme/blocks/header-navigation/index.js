( function ( blocks, element ) {
	blocks.registerBlockType( 'esc-river-rats/header-navigation', {
		edit: function () {
			return element.createElement( 'div', { className: 'esc-header-editor-placeholder' }, 'Header-Navigation (wird automatisch aus ESC → Header ausgegeben)' );
		},
		save: function () { return null; }
	} );
} )( window.wp.blocks, window.wp.element );
