import {OnInit, OnDestroy} from "@angular/core";
import {ActivatedRoute} from "@angular/router";
import {Component} from "@angular/core";
import {TitleService, TitleBarLink, NavBackService} from "@synerty/peek-util";
import {VortexStatusService} from "@synerty/vortexjs";

@Component({
    selector: "peek-main-title",
    templateUrl: "main-title.component.dweb.html",
    styleUrls: ["main-title.component.dweb.scss"],
    moduleId: module.id
})
export class MainTitleComponent implements OnInit, OnDestroy {

    private subscriptions: any[] = [];

    private leftLinks = [];
    private rightLinks = [];

    title: string = "Peek";
    isEnabled: boolean = true;
    vortexIsOnline:boolean= false;

    constructor(vortexStatusService:VortexStatusService,
                titleService: TitleService) {
        this.leftLinks = titleService.leftLinksSnapshot;
        this.rightLinks = titleService.rightLinksSnapshot;

        this.subscriptions.push(
            titleService.title.subscribe(v => this.title = v));

        this.subscriptions.push(
            titleService.isEnabled.subscribe(v => this.isEnabled = v));

        this.subscriptions.push(
            titleService.leftLinks.subscribe(v => this.leftLinks = v));

        this.subscriptions.push(
            titleService.rightLinks.subscribe(v => this.rightLinks = v));

        this.subscriptions.push(
            vortexStatusService.isOnline.subscribe(v => this.vortexIsOnline = v));

    }

    ngOnInit() {
    }

    ngOnDestroy() {
        while (this.subscriptions.length > 0)
            this.subscriptions.pop().unsubscribe();
    }

    // ------------------------------
    // Display methods

    linkTitle(title:TitleBarLink) {
        if (title.badgeCount == null) {
            return title.text;
        }

        if (title.left) {
            return `${title.text} (${title.badgeCount})`;
        }

        return `(${title.badgeCount}) ${title.text}`;

    }
}

