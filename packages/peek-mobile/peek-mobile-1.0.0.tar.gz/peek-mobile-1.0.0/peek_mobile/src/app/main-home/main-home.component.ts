import {Component, OnInit} from "@angular/core";
import {
    ComponentLifecycleEventEmitter,
    TupleDataOfflineObserverService
} from "@synerty/vortexjs";
import {TitleService} from "@synerty/peek-util";
import {homeLinks} from "../../plugin-home-links";


@Component({
    selector: "peek-main-home",
    templateUrl: 'main-home.component.web.html',
    moduleId: module.id
})
export class MainHomeComponent extends ComponentLifecycleEventEmitter implements OnInit {

    appDetails = homeLinks;

    constructor(titleService: TitleService) {
        super();
        titleService.setTitle("Peek Home");

    }

    ngOnInit() {
    }

    appButtonGridColumns = 3;

    appButtonGridRows(): string {
        let val = "auto";
        for (let i = 0; i < this.appDetails.length / this.appButtonGridColumns; i++) {
            val += ", auto";
        }
        return val;
    }

    appButtonGridRowIndex(index): number {
        return Math.floor(index / this.appButtonGridColumns);
    }

}

