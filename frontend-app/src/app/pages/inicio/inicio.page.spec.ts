import type { ComponentFixture } from '@angular/core/testing';
import { TestBed } from '@angular/core/testing';

import { InicioPage } from './inicio.page';

describe('InicioPage', () => {
  let fixture: ComponentFixture<InicioPage>;

  beforeEach(() => {
    fixture = TestBed.createComponent(InicioPage);
    fixture.detectChanges();
  });

  it('muestra el nombre de la plataforma', () => {
    const titulo = (fixture.nativeElement as HTMLElement).querySelector('h1');
    expect(titulo?.textContent).toContain('Radio Colaborativa');
  });
});
