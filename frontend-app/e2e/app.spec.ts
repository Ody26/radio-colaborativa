import { expect, test } from '@playwright/test';

test('muestra la página de inicio', async ({ page }) => {
  await page.goto('/');
  await expect(page.locator('#contenedor')).toContainText('Radio Colaborativa');
});
