def apply_filter(image, filter_type):
    from PIL import ImageFilter

    if filter_type == 'BLUR':
        return image.filter(ImageFilter.BLUR)
    elif filter_type == 'CONTOUR':
        return image.filter(ImageFilter.CONTOUR)
    elif filter_type == 'DETAIL':
        return image.filter(ImageFilter.DETAIL)
    elif filter_type == 'EDGE_ENHANCE':
        return image.filter(ImageFilter.EDGE_ENHANCE)
    elif filter_type == 'EMBOSS':
        return image.filter(ImageFilter.EMBOSS)
    elif filter_type == 'SHARPEN':
        return image.filter(ImageFilter.SHARPEN)
    else:
        raise ValueError(f"Unknown filter type: {filter_type}")