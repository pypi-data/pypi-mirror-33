import {NgModule, NgModuleFactoryLoader, NO_ERRORS_SCHEMA} from "@angular/core";
import {CommonModule} from "@angular/common";
import {NativeScriptModule} from "nativescript-angular/nativescript.module";
import {NativeScriptFormsModule} from "nativescript-angular/forms";
import {
    NativeScriptRouterModule,
    NSModuleFactoryLoader
} from "nativescript-angular/router";
// @synerty
import {Ng2BalloonMsgNsModule} from "@synerty/ng2-balloon-msg-ns";
import {PeekModuleFactory} from "@synerty/peek-util-ns";
import {
    TupleActionPushOfflineSingletonService,
    TupleStorageFactoryService,
    WebSqlFactoryService
} from "@synerty/vortexjs";

import {
    TupleStorageFactoryServiceNs,
    WebSqlNativeScriptThreadedFactoryService
} from "@synerty/vortexjs/index-nativescript";
// Routes
import {staticRoutes} from "./app/app.routes";
// Providers
import {peekRootServices} from "./app/app.services";
// Components
import {AppComponent} from "./app/app.component";
import {MainHomeComponent} from "./app/main-home/main-home.component";
import {MainConfigComponent} from "./app/main-config/main-config.component";
import {MainTitleComponent} from "./app/main-title/main-title.component";
import {UnknownRouteComponent} from "./app/unknown-route/unknown-route.component";
import {pluginRootModules} from "./plugin-root-modules";
import {pluginRootServices} from "./plugin-root-services";
// Add FontAwesome
import {TNSFontIconModule, TNSFontIconService} from "nativescript-ngx-fonticon";
import {Page} from "ui/page";
import {MainFooterComponent} from "./app/main-footer/main-footer.component";
// turn debug on

TNSFontIconService.debug = false;


@NgModule({
    declarations: [AppComponent,
        MainTitleComponent,
        MainFooterComponent,
        MainHomeComponent,
        MainConfigComponent,
        UnknownRouteComponent],
    bootstrap: [AppComponent],
    imports: [
        CommonModule,
        NativeScriptModule,
        NativeScriptFormsModule,
        NativeScriptRouterModule,
        PeekModuleFactory.RouterModule.forRoot(staticRoutes),
        Ng2BalloonMsgNsModule,
        ...pluginRootModules,
        TNSFontIconModule.forRoot({
            // Webpack doesn't import this if it's in assets
            'fa': './fonts/font-awesome.min.css'
        })
    ],
    schemas: [NO_ERRORS_SCHEMA],
    providers: [
        ...peekRootServices,

        {provide: NgModuleFactoryLoader, useClass: NSModuleFactoryLoader},
        {
            provide: WebSqlFactoryService,
            useClass: WebSqlNativeScriptThreadedFactoryService
        },
        {provide: TupleStorageFactoryService, useClass: TupleStorageFactoryServiceNs},
        TupleActionPushOfflineSingletonService,


        ...pluginRootServices,
    ]
})
export class AppNsModule {
    constructor(page: Page) {
        page.actionBarHidden = true;
    }

}
