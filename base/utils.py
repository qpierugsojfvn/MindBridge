# def custom_slugify(value):
#     # Replace spaces with hyphens and preserve special characters like '+'
#     return value.replace(' ', '-')

def custom_slugify_(value):
    value = value.lower()
    return value.replace('+', '%2B')