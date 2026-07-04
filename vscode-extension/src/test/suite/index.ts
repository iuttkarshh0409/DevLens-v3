import * as path from 'path';
import * as fs from 'fs';
import Mocha from 'mocha';

export function run(): Promise<void> {
  const mocha = new Mocha({
    ui: 'tdd',
    color: true
  });

  const testsRoot = path.resolve(__dirname, '..');

  return new Promise((c, e) => {
    try {
      const getFiles = (dir: string): string[] => {
        let results: string[] = [];
        const list = fs.readdirSync(dir);
        list.forEach(file => {
          const filePath = path.join(dir, file);
          const stat = fs.statSync(filePath);
          if (stat && stat.isDirectory()) {
            results = results.concat(getFiles(filePath));
          } else if (file.endsWith('.test.js')) {
            results.push(filePath);
          }
        });
        return results;
      };

      const files = getFiles(testsRoot);
      files.forEach(f => mocha.addFile(f));

      mocha.run(failures => {
        if (failures > 0) {
          e(new Error(`${failures} tests failed.`));
        } else {
          c();
        }
      });
    } catch (err) {
      e(err as Error);
    }
  });
}
