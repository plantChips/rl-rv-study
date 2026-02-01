package edu.rvpaper.classifier;

import edu.rvpaper.CSVGenerator;
import edu.rvpaper.MethodSamplePair;

import java.util.*;

public class Classifier {

    protected List<MethodSamplePair> methodsList;
    protected final List<List<String>> mainEvents;
    protected final List<String> projectPackages;
    protected final Set<String> nativeMethods;
    int valid_events = 0;

    private static final List<String> ASPECTJ_CFLOW_PREFIX = Arrays.asList(
        "org.aspectj.runtime.internal.cflowstack.ThreadStackFactoryImpl.ThreadCounterImpl.initialValue",
        "java.lang.ThreadLocal.setInitialValue",
        "java.lang.ThreadLocal.get",
        "org.aspectj.runtime.internal.cflowstack.ThreadStackFactoryImpl.ThreadCounterImpl.getThreadCounter",
        "org.aspectj.runtime.internal.cflowstack.ThreadStackFactoryImpl.ThreadCounterImpl.inc",
        "org.aspectj.runtime.internal.CFlowCounter.inc"
    );

    public Classifier(List<List<String>> allEvents, List<List<String>> mainEvents, List<String> projectPackages, Set<String> nativeMethods) {
        this.mainEvents = mainEvents;
        this.projectPackages = projectPackages;
        this.nativeMethods = nativeMethods;
        processEventsForClassifier();
    }

    public void processEventsForClassifier() {
        if (mainEvents == null) {
            System.out.println("[ERROR] mainEvents is null");
            return;
        }

        Set<Category> categories = new HashSet<>(Arrays.asList(
                Category.ASPECTJ,
                Category.MONITORING,
                Category.SPECIFICATION,
                Category.VALG,
                Category.RVMONITOR,
                Category.PROJECT
        ));

        HashMap<Category, Integer> counter = new HashMap<>();

        for (List<String> event : mainEvents) {

            if (event == null) {
                System.out.println("[ERROR] Encountered null event in mainEvents");
                continue;
            }
            if (event.size() >= ASPECTJ_CFLOW_PREFIX.size() && 
                event.subList(0, ASPECTJ_CFLOW_PREFIX.size()).equals(ASPECTJ_CFLOW_PREFIX)) {
                event = new ArrayList<>(event.subList(ASPECTJ_CFLOW_PREFIX.size(), event.size()));  
            }
            for (int i = 0; i <= event.size() - 4; i++) {
                if (event.get(i).startsWith("org.aspectj.runtime.internal.cflowstack.ThreadStackFactoryImpl.ThreadCounterImpl") &&
                    event.get(i + 1).startsWith("org.aspectj.runtime.internal.cflowstack.ThreadStackFactoryImpl.ThreadCounterImpl") &&
                    event.get(i + 2).startsWith("org.aspectj.runtime.internal.CFlowCounter") &&
                    event.get(i + 3).contains("sampleGamma")) {
                        event.subList(i, i+3).clear();
                        break;
                }
            }
            if (!event.isEmpty()) {
                valid_events += 1;

                boolean found = false;
                Category foundCategory = Category.OTHER;

                for (String methodName : event) {

                    if (methodName == null) {
                        System.out.println("[ERROR] Null method name inside event: " + event);
                        continue;
                    }

                    Category methodCategory;
                    try {
                        methodCategory = classifyMethod(methodName);
                    } catch (Exception e) {
                        System.out.println("[ERROR] Exception during classifyMethod for: " + methodName);
                        e.printStackTrace();
                        continue;
                    }

                    if (categories.contains(methodCategory)) {
                        foundCategory = methodCategory;
                        found = true;
                        break;
                    }
                }

                if (!found) {
                    counter.put(Category.OTHER,
                            counter.getOrDefault(Category.OTHER, 0) + 1);
                } else {
                    counter.put(foundCategory,
                            counter.getOrDefault(foundCategory, 0) + 1);
                }
            } else {
                System.out.println("[DEBUG] Empty event encountered");
            }
        }

        methodsList = new ArrayList<>();

        if (counter.isEmpty()) {
            System.out.println("[WARNING] Counter is empty after processing events");
        }

        for (Map.Entry<Category, Integer> set : counter.entrySet()) {
            if (set.getKey() == null) {
                System.out.println("[ERROR] Null category key in counter");
                continue;
            }
            methodsList.add(new MethodSamplePair(set.getKey(), set.getValue()));
        }

        try {
            methodsList.sort((a, b) -> b.sample - a.sample);
        } catch (Exception e) {
            System.out.println("[ERROR] Exception while sorting methodsList");
            e.printStackTrace();
        }
    }

    public Category classifyMethod(String method) {
        if (method == null) {
            System.out.println("[ERROR] classifyMethod received null method");
            return Category.OTHER;
        }

        if (method.startsWith("org.aspectj.")) {
            return Category.ASPECTJ;
        } else if (method.startsWith("mop.")) {
            if (method.contains("MonitorAspect")) {
                return Category.SPECIFICATION;
            }
            if (method.startsWith("mop.MultiSpec") || method.contains("Monitor.") || 
                method.contains("Monitor_Set.") || method.contains("DisableHolder")) {
                return Category.MONITORING;
            }
            System.out.println("[!] Need to Classify " + method);
            return Category.OTHER;
        } else if (method.startsWith("com.runtimeverification.rvmonitor.java.rt.rlagent.")
                || method.startsWith("com.runtimeverification.rvmonitor.java.rt.agent")) {
            return Category.VALG;
        } else if (method.startsWith("com.runtimeverification.rvmonitor.")) {
            return Category.RVMONITOR;
        }

        if (projectPackages == null) {
            return Category.OTHER;
        }

        for (String projectPackage : projectPackages) {
            if (projectPackage == null) {
                System.out.println("[ERROR] Null entry in projectPackages");
                continue;
            }
            if (method.startsWith(projectPackage)) {
                return Category.PROJECT;
            }
        }

        return Category.OTHER;
    }

    public void classify() {}

    public void output() {
        try {
            new CSVGenerator().output("output.csv", methodsList, Category.getDefault(), new String[]{valid_events + ""});
        } catch (Exception ignored) {}
    }
}
