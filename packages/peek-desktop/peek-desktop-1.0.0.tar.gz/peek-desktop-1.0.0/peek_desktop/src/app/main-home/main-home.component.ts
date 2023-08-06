import {Component, OnInit} from "@angular/core";
import {ComponentLifecycleEventEmitter} from "@synerty/vortexjs";
import {TitleService, NavBackService} from "@synerty/peek-util";


@Component({
    selector: "peek-main-home",
    templateUrl: 'main-home.component.dweb.html',
    styleUrls: ["main-home.component.dweb.scss"],
    moduleId: module.id
})
export class MainHomeComponent extends ComponentLifecycleEventEmitter {

    constructor(titleService: TitleService,
                public navBackService: NavBackService) {
        super();
        titleService.setTitle("Peek Home");

    }


}

