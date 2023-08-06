import {platformBrowserDynamic} from "@angular/platform-browser-dynamic";

// Potentially enable angular prod mode
import {enableProdMode} from "@angular/core";
import {environment} from "environments/environment";

import {VortexService} from "@synerty/vortexjs";
VortexService.setVortexClientName("peek-desktop");

if (environment.production) {
    enableProdMode();
}

import {AppWebModule} from "./app.web.module";
platformBrowserDynamic().bootstrapModule(AppWebModule);

