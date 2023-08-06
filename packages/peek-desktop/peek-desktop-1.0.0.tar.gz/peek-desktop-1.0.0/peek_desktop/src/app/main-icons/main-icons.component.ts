import {Component, OnInit} from "@angular/core";
import {
    ComponentLifecycleEventEmitter,
    TupleDataOfflineObserverService
} from "@synerty/vortexjs";
import {TitleService} from "@synerty/peek-util";
import {homeLinks} from "../../plugin-home-links";


@Component({
    selector: "peek-main-icons",
    templateUrl: 'main-icons.component.dweb.html',
    styleUrls: ["main-icons.component.dweb.scss"],
    moduleId: module.id
})
export class MainIconsComponent extends ComponentLifecycleEventEmitter {

    appDetails = homeLinks;

    constructor() {
        super();

    }


}

