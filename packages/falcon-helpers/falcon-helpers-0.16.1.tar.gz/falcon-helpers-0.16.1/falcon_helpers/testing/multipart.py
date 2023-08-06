import mimetypes
import random
import string


_BOUNDARY_CHARS = string.digits + string.ascii_letters


def encode_multipart(fields, files, boundary=None):
    """Create a multi-part http request

    Original was found here with an MIT license:
        http://code.activestate.com/recipes/578668-encode-multipart-form-data-for-uploading-files-via/

    Encode dict of form fields and dict of files as multipart/form-data. Return tuple of
    (body_string, headers_dict).

    Each value in files is a dict with required keys 'filename' and 'content', and optional
    'mimetype' (if not specified, tries to guess mime type or uses 'application/octet-stream').
    """

    def escape_quote(s):
        return s.replace('"', '\\"')

    if boundary is None:
        boundary = ''.join(random.choice(_BOUNDARY_CHARS) for i in range(30))

    lines = []

    for name, value in fields.items():
        lines.extend((
            f'--{boundary}',
            f'Content-Disposition: form-data; name="{escape_quote(name)}"',
            '',
            value,
        ))

    for name, value in files.items():
        filename = value['filename']
        mimetype = (value.get('mimetype') or
                    mimetypes.guess_type(filename)[0] or
                    'application/octet-stream')
        name, filename = escape_quote(name), escape_quote(filename)

        lines.extend((
            f'--{boundary}',
            f'Content-Disposition: form-data; name="{name}"; filename="{filename}"',
            f'Content-Type: {mimetype}',
            '',
            value['content'],
        ))

    lines.extend((
        f'--{boundary}--',
        '',
    ))
    body = '\r\n'.join(lines)

    headers = {
        'Content-Type': f'multipart/form-data; boundary={boundary}',
        'Content-Length': str(len(body)),
    }

    return (body, headers)
