import { ServiceManager, ContentsManager } from '@jupyterlab/services';
export declare class JupyterService {
    serviceManager: ServiceManager;
    contentsManager: ContentsManager;
    setServiceManager(serviceManager: ServiceManager): void;
    setContentsManager(contentsManager: ContentsManager): void;
}
