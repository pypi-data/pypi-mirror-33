from pywebpack import WebpackBundle
js = WebpackBundle(
    "my_thing",
    entry={
        'datasource_link': './src/redash_stmo/js/datasource_link/somefile.js',
    },
)