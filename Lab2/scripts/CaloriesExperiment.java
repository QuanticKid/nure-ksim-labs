import org.nlogo.headless.HeadlessWorkspace;
import java.io.PrintWriter;

/**
 * ЛР2, експеримент 2: вплив калорійності купки на вибір джерела їжі.
 *
 * Для кожної розстановки купок (random-seed 1..N) модель проганяється з калорійністю
 * купки №1 = 1..5 (calorie-mode = "one rich"). Купки стоять на тих самих місцях,
 * змінюється лише калорійність, тому порівняння коректне.
 *
 * Запуск (див. README.md):
 *   java -cp "D:/NetLogo 6.4.0/app/netlogo-6.4.0.jar" CaloriesExperiment.java ../Ants_modified.nlogo ../lab2_calories_raw.csv 30
 */
public class CaloriesExperiment {
  public static void main(String[] args) throws Exception {
    String model = args[0], out = args[1];
    int seeds = args.length > 2 ? Integer.parseInt(args[2]) : 30;
    int[] values = {1, 2, 3, 4, 5};

    HeadlessWorkspace ws = HeadlessWorkspace.newInstance();
    ws.open(model);
    try (PrintWriter w = new PrintWriter(out, "UTF-8")) {
      w.println("seed,rich_value,rich_pile_rank_by_distance,rich_pile_distance,"
          + "share_from_rich_first_400_ticks,ticks_rich_pile_exhausted,ticks_all_food_collected");
      for (int s = 1; s <= seeds; s++) {
        for (int v : values) {
          ws.command("random-seed " + s);
          ws.command("set population 125 set food-sources 3 set reproduction? false set starvation? false "
              + "set diffusion-rate 50 set evaporation-rate 10 "
              + "set calorie-mode \"one rich\" set max-value " + v);
          ws.command("setup");

          // відстань купки №1 до гнізда
          double dist1 = num(ws.report("mean [distancexy 0 0] of patches with [food-source-number = 1]"));

          double share = -1, tRich = -1;
          while (true) {
            ws.command("repeat 10 [ go ]");
            double t = num(ws.report("ticks"));
            // частка порцій з багатої купки за перші 400 тактів
            if (share < 0 && t >= 400)
              share = num(ws.report("ifelse-value (sum delivered = 0) [0] [first delivered / sum delivered]"));
            // такт, коли багату купку зібрано повністю
            if (tRich < 0 && !(Boolean) ws.report("any? patches with [food-source-number = 1 and food > 0]"))
              tRich = t;
            if (!(Boolean) ws.report("any? patches with [food > 0]") || t >= 20000) {
              if (share < 0) share = num(ws.report("first delivered / sum delivered"));
              if (tRich < 0) tRich = t;
              // місце купки №1 серед трьох за відстанню до гнізда (1 - найближча, 3 - найдальша).
              // Рахується після прогону: "[...] of patches" перебирає клітинки у випадковому порядку
              // і витрачає випадкові числа, тож до прогону воно змінило б результати.
              int rank = (int) num(ws.report(
                  "1 + length filter [ d -> d < " + dist1 + " ] "
                  + "map [ n -> mean [distancexy 0 0] of patches with [food-source-number = n] ] [2 3]"));
              w.printf("%d,%d,%d,%.1f,%.4f,%.0f,%.0f%n", s, v, rank, dist1, share, tRich, t);
              w.flush();
              break;
            }
          }
        }
        System.out.println("seed " + s + " done");
      }
    }
    ws.dispose();
    System.exit(0);
  }

  private static double num(Object o) { return ((Number) o).doubleValue(); }
}
