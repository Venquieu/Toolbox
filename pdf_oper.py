# Refer to the documentation for more details: https://pypdf.readthedocs.io/en/latest/index.html
# pip install pypdf2

import PyPDF2 as pypdf


class PdfOperator(object):
    def __init__(self, file_path: str) -> None:
        self.file_path = file_path
        with open(file_path, 'rb') as f:
            self.reader = pypdf.PdfReader(f)
        self.pages = self.reader.pages

        self.__metadata = {
            "author": self.reader.metadata.author,
            "creator": self.reader.metadata.creator,
            "producer": self.reader.metadata.producer,
            "subject": self.reader.metadata.subject,
            "title": self.reader.metadata.title,
            "npages": len(self.pages),
        }

    def rorate(self, page_idx: int, angle: int) -> None:
        """
        Rotates the specified page clockwise by the specified angle.\n
        Args:
            page_idx: The page number to rotate.
            angle: The angle in clockwise to rotate the page by.
        """
        page = self.pages[page_idx]
        angle = angle % 360
        if angle >= 0:
            page = page.rotateClockwise(angle)
        else:
            page = page.rotateCounterClockwise(-angle)
        self.pages[page_idx] = page

    def delete(self, page_idx: int) -> None:
        """
        Deletes the specified page.\n
        Args:
            page_idx: The page number to delete.
        """
        self.pages[page_idx] = None
        self.__metadata["npages"] -= 1

    def append(self, file_path: str) -> None:
        """
        Appends the specified PDF file to the current PDF file.\n
        Args:
            file_path: The path of the PDF file to append.
        """
        reader = pypdf.PdfReader(file_path)
        self.pages.extend(reader.pages)
        self.__metadata["npages"] += len(reader.pages)

    def save(self, file_path: str = None) -> None:
        """
        Saves the current PDF file to the specified file path or the original file path if not specified.\n
        Args:
            file_path: The path of the file to save the PDF to.
        """
        file_path = file_path or self.file_path

        writer = pypdf.PdfWriter()
        for page in self.pages:
            if page is not None:
                writer.addPage(page)

        with open(file_path, 'wb') as f:
            writer.write(f)

    @property
    def meta(self) -> dict:
        return self.__metadata
