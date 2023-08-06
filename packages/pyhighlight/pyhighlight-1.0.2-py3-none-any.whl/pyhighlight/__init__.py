name = 'pyhighlight'
import matplotlib.pyplot as pyplot
import matplotlib.patches as patches

class InvalidImagePathError(Exception):
    def __init__(self, message):
        super().__init__(message)

class EmptyPointsError(Exception):
    def __init__(self, message):
        super().__init__(message)

class InvalidTransparencyValueError(Exception):
    def __init__(self, message):
        super().__init__(message)


class pyhighlight:
    def __init__(self, image_path):
        try:
            image = pyplot.imread(image_path)
            height, width, nbands = image.shape
            fig_size = width / float(80), height / float(80)
            figure = pyplot.figure(figsize=fig_size)
            self.final_image = figure.add_axes([0, 0, 1, 1])
            self.final_image.axis('off')
            self.final_image.imshow(image, interpolation='nearest')

        except FileNotFoundError:
            raise InvalidImagePathError('Could not open ' + image_path)
    
    def highlight(self, points, color='blue', transparency=0.3):
        if not points or points == []:
            raise EmptyPointsError('A valid array of points must be provided')
        
        if transparency > 1 or transparency < 0:
            raise InvalidTransparencyValueError('Transparency must be a value between 0 and 1')

        shape = pyplot.Polygon(points, closed=True, alpha=transparency, fill=True, color=color)
        self.final_image.add_patch(shape)
    
    def save(self, path='pyhighlight-output.png', transparent=True):
        generated_image = pyplot.gcf()
        pyplot.draw()
        generated_image.savefig(path, dpi=80, transparent=transparent)
