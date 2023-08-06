import {platformBrowserDynamic} from "@angular/platform-browser-dynamic";



// Enable the use of workers for the payload
import {Payload} from "@synerty/vortexjs";
import {PayloadDelegateWeb} from "@synerty/vortexjs/index-browser";

import {VortexService} from "@synerty/vortexjs";
VortexService.setVortexClientName("peek-mobile");

// Payload.setWorkerDelegate(new PayloadDelegateWeb());

// Potentially enable angular prod mode
import {enableProdMode} from "@angular/core";
import {environment} from "environments/environment";

if (environment.production) {
    enableProdMode();
}

import {AppWebModule} from "./app.web.module";
platformBrowserDynamic().bootstrapModule(AppWebModule);


