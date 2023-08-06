from guillotina import configure


app_settings = {
}


def includeme(root):
    """
    custom application initialization here
    """
    configure.scan('guillotina_batch.api')
