/// <reference types="markdown-it" />
import { OnInit, AfterViewInit, ViewContainerRef, Compiler, ElementRef } from '@angular/core';
import { PromiseDelegate } from '@phosphor/coreutils';
import * as MarkdownIt from 'markdown-it';
import { FileService } from '../services/file.service';
import { IFormComponent } from './create-form-component-factory';
export declare class FormBuilderComponent implements OnInit, AfterViewInit {
    private compiler;
    private myFileService;
    myMarkdownIt: MarkdownIt.MarkdownIt;
    viewInitialised: PromiseDelegate<void>;
    errorbox: ElementRef<HTMLDivElement>;
    telemetry: ElementRef<HTMLIFrameElement>;
    container: ViewContainerRef;
    errorboxDiv: HTMLDivElement;
    private formComponentRef;
    constructor(compiler: Compiler, myFileService: FileService);
    ngOnInit(): void;
    ngAfterViewInit(): void;
    private _setUsageStatistics(string);
    /**
     * Set or update the template of the form.
     *
     * This function makes sure to only begin building the form once the component
     * has sufficiently initialised.
     */
    buildForm(markdownTemplate: string): Promise<IFormComponent>;
    stripStyleTags(html: string): string[];
    /**
     * Convert the form template from markdown to its final html state.
     *
     * @param markdownTemplate The markdown template.
     *
     * @returns The html template.
     */
    private convertTemplate(markdownTemplate);
    /**
     * Create the form component from the html template with the Angular compiler.
     *
     * @param template The html Angular component template
     */
    private createFormFromTemplate(template, cssStyles);
}
