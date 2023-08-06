import {Component} from "@angular/core";
import {
    ConfigLink,
    FooterService,
    NavBackService,
    TitleService
} from "@synerty/peek-util";
import {ComponentLifecycleEventEmitter, VortexStatusService} from "@synerty/vortexjs";

@Component({
    selector: "peek-main-footer",
    templateUrl: "main-footer.component.dweb.html",
    styleUrls: ["main-footer.component.dweb.scss"],
    moduleId: module.id
})
export class MainFooterComponent extends ComponentLifecycleEventEmitter {

    configLinks: ConfigLink[] = [];

    vortexIsOnline: boolean = false;
    statusText: string = "";
    isEnabled: boolean = true;

    constructor(vortexStatusService: VortexStatusService,
                footerService: FooterService,
                titleService: TitleService,
                private navBackService: NavBackService) {
        super();

        this.configLinks = footerService.configLinksSnapshot;

        footerService.statusText
            .takeUntil(this.onDestroyEvent)
            .subscribe(v => this.statusText = v);

        titleService.isEnabled
            .takeUntil(this.onDestroyEvent)
            .subscribe(v => this.isEnabled = v);

        footerService.configLinks
            .takeUntil(this.onDestroyEvent)
            .subscribe(v => this.configLinks = v);

        vortexStatusService.isOnline
            .takeUntil(this.onDestroyEvent)
            .subscribe(v => this.vortexIsOnline = v);

    }

    isBackButtonEnabled(): boolean {
        return this.navBackService.navBackLen() != 0;
    }
}

