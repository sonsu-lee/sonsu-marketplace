# Accessibility checks

접근성은 별도 마감 단계가 아니라 G2, G4, G5와 함께 구현하고 G6에서 실제 증거로 판정한다.

## 필수 검사

- keyboard만으로 primary path와 모든 interactive control에 도달한다.
- focus indicator가 배경과 구분되고 잘리지 않는다.
- icon-only control, status, input과 error에 accessible name 또는 programmatic relation이 있다.
- 현재 selection, expanded, disabled, invalid와 loading 상태가 semantic state로 노출된다.
- status와 error를 색만으로 전달하지 않는다.
- text, icon, focus와 interactive boundary의 contrast를 실제 사용 색 조합으로 검사한다.
- table header, row/cell relationship, sorting state와 bulk selection label이 의미 있게 노출된다.
- dialog/drawer의 name, focus entry, focus containment와 return focus를 확인한다.

자동화 도구가 없으면 keyboard와 semantics는 수동 관찰 기록을 남길 수 있다. 필요한 검사를 수행하지 않은 경우 `passed`가 아니라 `not_run` 또는 `inconclusive`다.
