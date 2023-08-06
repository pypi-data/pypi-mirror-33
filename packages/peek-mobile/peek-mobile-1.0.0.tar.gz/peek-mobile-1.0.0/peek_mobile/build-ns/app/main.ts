// this import should be first in order to load some required settings (like globals and reflect-metadata)
import {platformNativeScriptDynamic} from "nativescript-angular/platform";

// -----------------------------
// Import and set the vortexjs, and the vortex connection
import "nativescript-websockets";
import "moment";

import 'rxjs/add/observable/zip';
import 'rxjs/add/observable/interval';
import 'rxjs/add/operator/map';
import 'rxjs/add/operator/zip';
import 'rxjs/add/operator/filter';
import 'rxjs/add/operator/takeUntil';
import 'rxjs/add/operator/first';
import 'rxjs/add/operator/toPromise';
import 'rxjs/add/operator/debounce';


// -----------------------------
// Import and set the vortexjs, and the vortex connection
import "@synerty/vortexjs";

import {VortexService} from "@synerty/vortexjs";
VortexService.setVortexUrl(null);
VortexService.setVortexClientName("peek-mobile");

// -----------------------------
// Enable the use of workers for the payload
import {Payload} from "@synerty/vortexjs";
import {PayloadDelegateNs} from "@synerty/vortexjs/index-nativescript";

Payload.setWorkerDelegate(new PayloadDelegateNs());

// -----------------------------
// Enavble the IQ Keyboard
// import  "nativescript-iqkeyboardmanager";
// const iqKeyboard = IQKeyboardManager.sharedManager();
// iqKeyboard.overrideKeyboardAppearance = true;
// iqKeyboard.keyboardAppearance = UIKeyboardAppearance.Dark;

// -----------------------------
// Enable production angular

// import "nativescript-angular";
// // Potentially enable angular prod mode
// import {enableProdMode} from "@angular/core";
// import {environment} from "../src/environments/environment";
//
// if (environment.production) {
//     enableProdMode();
// }


// -----------------------------
// Bootstrap the app
// This should be last
import {AppNsModule} from "./app.ns.module";

platformNativeScriptDynamic().bootstrapModule(AppNsModule);
