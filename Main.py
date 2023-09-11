import time
import json
import shutil
import os
from plyer import notification
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

with open("Setting.json","r") as f:
    setting_data = json.load(f)

def get_path(file):
        found = False
        _,file_extension = os.path.splitext(file)
        for folder,extensions in setting_data['folders'].items():
            if file_extension in extensions:
                dest_path=os.path.join(setting_data['source'],folder)
                found = True
                break
        if not found:
            dest_path = os.path.join(setting_data['source'],'other')

        return dest_path

class Watcher:

    def __init__(self):
        self.folder=[]
        self.check_source()
        self.observer = Observer()


    def check_source(self):
        # create folder if the the folder doesnt exist 
        for folder in setting_data['folders']:
            self.folder.append(folder)
            folder_path = os.path.join(setting_data['source'],folder)
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)

        # loop through the folder and move the file to certain location by extensions
        with os.scandir(setting_data['source']) as entries:
            for entry in entries:
                filename = entry.name
                #skip the folder that u just created, to prevent move folder to "other"
                if filename not in self.folder:
                    try:
                        dest_path=get_path(filename)
                        shutil.move(entry.path, dest_path)
                        

                    except shutil.Error as e:
                        start_quote = str(e).rfind("\\")
                        end_quote = str(e).rfind("'")
                        filename = str(e)[start_quote + 1:end_quote]
                        # os.remove(os.path.join(source_dir,filename))
                        print(f' Something wrong with {filename}')
                        print(e)

            print('Folder has been Organized')


    def run(self):
        event_handler = Handler()
        self.observer.schedule(event_handler, setting_data['source'], recursive=True)
        self.observer.start()
        try:
            while True:
                time.sleep(5)
        except:
            self.observer.stop()
            print('STOPPED')

        self.observer.join()


class Handler(FileSystemEventHandler):
    
    # @staticmethod
    def on_any_event(self,event):
        # if event.is_directory:
        #     return None

        if event.event_type == 'created':
            dest_path = get_path(file=event.src_path)
            filename,extension = os.path.splitext(event.src_path)
            shutil.move(event.src_path, dest_path)
            notification.notify(
                title='File Alert',
                message=f'{filename} has been moved to {dest_path}',
                timeout=5
                ) 

        elif event.event_type == 'modified':
            pass
        
        elif event.event_type == 'deleted':
            # Taken any action here when a file is deleted.
            filename = os.path.basename(event.src_path)
            notification.notify(
                title='File Alert',
                message=f'{filename} has been deleted',
                timeout=5
                )     


if __name__ == '__main__':
    w = Watcher()
    w.run()