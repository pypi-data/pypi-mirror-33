/* tslint:disable:no-unused-variable */
import { async, ComponentFixture, TestBed } from '@angular/core/testing';
import { By } from '@angular/platform-browser';
import { DebugElement } from '@angular/core';

import { EnvClientComponent } from './env-client.component';

describe('EnvClientComponent', () => {
  let component: EnvClientComponent;
  let fixture: ComponentFixture<EnvClientComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ EnvClientComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(EnvClientComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
