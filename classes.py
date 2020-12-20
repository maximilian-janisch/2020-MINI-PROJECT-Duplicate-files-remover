from abc import ABC, abstractmethod
import os, glob, shutil


class DuplicateRemover(ABC):
    def __init__(self, directory, glob_recursive=False, pattern="*.*"):
        """
        Initializes the DuplicateRemover class.
        :param directory: The base directory in which duplicates should be removed
        :param glob_recursive: Whether recursive in glob.glob should be True.
        :param pattern: Give your own pattern for glob.glob in `directory`. For example, that pattern could be
        `*.txt` or `**/*.txt` or `?.gif` etc.
        NOTE 1: USE `pattern="*.*"` for all files in the current directory and use `pattern="**/*.*"` togeher with
        glob_recursive=True if you want all files in all subdirectories of `directory` and all files in `directory`
        itself.
        NOTE 2: I am always using absolute paths here.
        """
        self.directory = os.path.abspath(directory)
        self.glob_recursive = glob_recursive
        self.pattern = pattern

    def __call__(self, directory_to_move_duplicates_to=None):
        """
        Moves duplicate files to a separate directory, while preserving the subdirectory structure in there.
        :param directory_to_move_duplicates_to: Each duplicate stored at directory/path will be moved to
        directory_to_move_duplicates_to/path.
        DEFAULT: directory_to_move_duplicates_to = directory/duplicates
        """
        if directory_to_move_duplicates_to is None:
            directory_to_move_duplicates_to = os.path.join(self.directory, "duplicates")
        directory_to_move_duplicates_to = os.path.join(os.path.abspath(directory_to_move_duplicates_to), "")
        # ^ ensures correct formatting

        classes = self.get_equivalence_classes()
        for equiv_class in classes:
            best_file = self.get_best_file_from_class(equiv_class)
            for file in equiv_class:
                if file == best_file:
                    continue
                dest = file.replace(self.directory, directory_to_move_duplicates_to)
                os.makedirs(os.path.dirname(dest), exist_ok=True)
                shutil.move(file, dest)

    @abstractmethod
    def check_duplicate(self, file_path1, file_path2):
        """
        Checks whether the files self.directory/file_path1 and self.directory/file_path2 are identical for our purposes.
        :param file_path1: File_path of the first file.
        :param file_path2: File_path of the second file
        :return: True if identical for our purposes (for example identical images up to rescaling).
        """
        pass

    @abstractmethod
    def get_best_file_from_class(self, file_class):
        """
        Determine which file out of a list of "identical for our purpose" files should be kept. For example, if
        "identical for our purpose" means "the same image up to rescaling", this function should return the image
        with the highest resolution.
        :param file_class: List of files that are identical according to check_duplicate.
        :return: Which file to keep
        """
        pass

    def get_files_to_consider(self):
        return glob.glob(os.path.join(self.directory, self.pattern), recursive=self.glob_recursive)

    def get_equivalence_classes(self):
        """
        Generates equivalence classes of the form [CLASS_1, CLASS_2, ..., CLASS_N],
        where each CLASS_k is a list of file paths that are pairwise identical according to self.check_duplicate.
        Overall, the sets are a proper (i.e. disjoint) cover of the list of files returned by self.get_files_to_consider.
        :return: List of lists.
        NOTE: I am fairly sure that the performance of this function could be improved.
        """
        classes = dict()  # first, we will create a dictionary like this: {file0: class0, file1: class0, file2: class1, etc.}.
        all_files = self.get_files_to_consider()

        for n in range(len(all_files)-1, -1, -1):  # go backwards from len(all_files)-1 to 0.
            file_to_classify = all_files.pop(n)  # pop the last file in all_files
            for file in classes.keys():  # classes.keys() are the currently classed images
                if self.check_duplicate(file_to_classify, file):  # if they are identical, assign the same class
                    classes[file_to_classify] = classes[file]
                    break
            else:  # only gets entered if `break` wasn't executed
                # Assign new class to file_to_classify as it isn't identical to any file that was classified so far
                classes[file_to_classify] = 0 if len(classes) == 0 else max(classes.values()) + 1

        # Restructure the classes data-structure
        return [[image for image in classes.keys() if classes[image] == k] for k in range(max(classes.values())+1)]


