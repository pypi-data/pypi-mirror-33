import { BehaviorSubject } from 'rxjs';
import { PromiseDelegate } from '@phosphor/coreutils';
import { Session, KernelMessage } from '@jupyterlab/services';
import { JupyterService } from './jupyter.service';
import { FileService } from './file.service';
export declare class WatchdogService {
    private myFileService;
    private myJupyterService;
    everythingIdle: PromiseDelegate<void>;
    session: Session.ISession;
    watchdogError: BehaviorSubject<KernelMessage.IErrorMsg>;
    fileChanged: BehaviorSubject<string>;
    constructor(myFileService: FileService, myJupyterService: JupyterService);
    startWatchdog(): void;
    watchdogFormUpdate(session: Session.ISession): void;
    addFilepathObserver(filepath: string): void;
}
