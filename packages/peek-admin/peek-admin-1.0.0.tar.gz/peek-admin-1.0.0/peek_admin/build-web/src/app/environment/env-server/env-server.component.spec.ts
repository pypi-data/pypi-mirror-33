/* tslint:disable:no-unused-variable */
import { async, ComponentFixture, TestBed } from '@angular/core/testing';
import { By } from '@angular/platform-browser';
import { DebugElement } from '@angular/core';

import { EnvServerComponent } from './env-server.component';

describe('EnvServerComponent', () => {
  let component: EnvServerComponent;
  let fixture: ComponentFixture<EnvServerComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ EnvServerComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(EnvServerComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
