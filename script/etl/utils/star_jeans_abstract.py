from abc import ABC, abstractmethod

class BasePipeline(ABC):

    @abstractmethod
    def showroom_collect(self):
        ...

    @abstractmethod
    def unique_colors_collect(self):
        ...

    @abstractmethod
    def individual_colors_collect(self):
        ...

    @abstractmethod
    def get_all_dataset(self):
        ...

    @abstractmethod
    def data_store(self):
        ...