/* tslint:disable:no-unused-variable */
import { async, ComponentFixture, TestBed } from '@angular/core/testing';
import { By } from '@angular/platform-browser';
import { DebugElement } from '@angular/core';

import { EnvAgentComponent } from './env-agent.component';

describe('EnvAgentComponent', () => {
  let component: EnvAgentComponent;
  let fixture: ComponentFixture<EnvAgentComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ EnvAgentComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(EnvAgentComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
