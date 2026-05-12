public class SwitchTest {

    private int switchCaseMethod() {

        int x = 3;

        switch (x) {

            case 1:
                x = 1;
                break;
            case 2:
                x = 2;
                break;
            case 3:
                x = 3;
                break;
            default:
                x = 4;
                break;
        }

        if (x == 3) {
            return 1 + 1;
        } else {
            return x;
        }

    }

}