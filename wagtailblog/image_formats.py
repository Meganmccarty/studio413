from wagtail.images.formats import Format, register_image_format, unregister_image_format

unregister_image_format('fullwidth')
register_image_format(Format('fullwidth', 'Full width (800px)', 'richtext-image full-width img-responsive', 'width-800'))

unregister_image_format('left')
register_image_format(Format('left', 'Left-aligned (400px)', 'richtext-image left img-responsive', 'width-400'))

unregister_image_format('right')
register_image_format(Format('right', 'Right-aligned (400px)', 'richtext-image right img-responsive', 'width-400'))

register_image_format(Format('center', 'Center-aligned (400px)', 'richtext-image center img-responsive', 'width-400'))
register_image_format(Format('left-float', 'Float Left (400px)', 'richtext-image float-left img-responsive', 'width-400'))
register_image_format(Format('right-float', 'Float Right (400px)', 'richtext-image float-right img-responsive', 'width-400'))