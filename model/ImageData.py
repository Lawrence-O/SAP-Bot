from torch.utils.data import Dataset
import cv2
from PIL import Image



class ImageDataset(Dataset):
    def __init__(self, image_paths,class_to_idx,transform=False):
        self.image_paths = image_paths
        self.transform = transform
        self.class_to_idx = class_to_idx
        
    def __len__(self):
        return len(self.image_paths)

    def __getitem__(self, idx):
        image_filepath = self.image_paths[idx]
        image = cv2.imread(image_filepath)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(image)

        label = image_filepath.split('/')[-2]
        label = self.class_to_idx[label]
        if self.transform:
            image = self.transform(image)
        
        return image, label