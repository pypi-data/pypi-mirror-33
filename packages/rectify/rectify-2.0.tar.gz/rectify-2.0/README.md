![rectify image](https://gitlab.com/jenx/rectify/raw/master/images/header.png "rectify")

# rectify

``rectify`` is a tiny Python package whose sole purpose of life is generating
randomized images with colorful bars on a single-color background. Making,
displaying and saving a picture like the one on the top of this page is as
simple as:

    from rectify.image import generate, save

    picture = generate(900, 30, background=(30, 30, 30), colors='pastel')

    picture.show()
    save(picture, 'bars.png')

Or from the command line:

    $ rectify -x 900 -y 30 -b '(30,30,30)' -c pastel -o 'bars.png' --show

Full documentation is available at
[jenx.gitlab.io/rectify](https://jenx.gitlab.io/rectify/).
