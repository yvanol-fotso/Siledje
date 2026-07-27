from dotenv import load_dotenv
load_dotenv()

from PySide6.QtCore import QCoreApplication
app = QCoreApplication([])

from src.managers.sync.cloud_data_sync_manager import CloudDataSyncManager

class FakeAdminUser:
    def has_permission(self, name):
        return True

mgr = CloudDataSyncManager(current_user=FakeAdminUser())
mgr.sync_finished.connect(lambda ok, msg: print(f"Résultat : {ok} — {msg}"))
mgr.sync_now()