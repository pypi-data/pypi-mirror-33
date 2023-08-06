import {Component} from "@angular/core";
import {TitleService} from "@synerty/peek-util";
import {configLinks} from "../../plugin-config-links";


@Component({
    selector: "peek-main-config",
    templateUrl: 'main-config.component.dweb.html',
    moduleId: module.id
})
export class MainConfigComponent {

    appDetails = configLinks;

    constructor(titleService: TitleService) {
        titleService.setTitle("Peek Config");

    }


}

