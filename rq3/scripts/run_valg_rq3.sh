#!/bin/bash

APPTAINER_CMD="/share/apps/software/apptainer/apptainer-1.4.0/bin/apptainer exec"
CONTAINER_PATHS="sandbox-valg-rq3"

SCRIPT_PATH="sandbox-valg-rq3/home/Valg/tracemop/scripts"
RESULTS_DIR="results-valg-rq3"
OUTPUT_DIR="outputs-valg-rq3"

projects=(
"agarciadom/xeger,f3b8a33b0f4438d639150b57b9a0257d50c71bc2"
"albfernandez/javadbf,395265f33bcf9080b02f2102c4b6284921cefae2"
"alibaba/QLExpress,456476288a9c0691b8890ff361605b1f7357acde"
"almondtools/stringsearchalgorithms,19f26f1c06192816b1ff2fb3b86740898d50a44d"
"almson/almson-refcount,ded7fe38d1e84f2af98f1d845d30fcc46aad197b"
"Antibrumm/jackson-antpathfilter,40f3af16e9a32fec910fadfde144c4b58217d5e7"
"asterisk-java/asterisk-java,84d890b8b852b6d3f14768ec651dbb710eacf57b"
"attoparser/attoparser,e1049dcd8261fe315b679029e711a9f5ea03f1cc"
"awslabs/route53-infima,cabce497698e41d610a949e8a5e4a0528170382b"
"brettwooldridge/SparseBitSet,8b32633706533a1fb828e05415dbdbc2c32f3a31"
"chocoteam/choco-graph,f4e7be389df244d4dd9138b81862e98efc9f4603"
"romix/java-concurrent-hash-trie-map,03335a9caa6fc867344c8c015d6dfc2d11ab062f"
"octavian-h/time-series-math,4fad82278e42307458a9faa46c2f13e2ac9816c6"
"codelion/gramtest,355cf41dcf0904e8d28aeb220241df0137c789ca"
"conveyal/osm-lib,4ff7fef141296ffe1d47a89ad40cefda7311566d"
"cowtowncoder/java-uuid-generator,31408f5c088d27766269f905896efe383b38a46e"
"danieldk/dictomaton,b23b48ba03ec43c0ce2ef1be85c0cbb8203a87b2"
"davidmoten/bplustree,761c1da3772772260520c41d9e9be8405931b4e5"
"davidmoten/rtree,f1da3d62dbdab20654b63da91510c51a32e8b8a8"
"davidmoten/rtree-multi,858da976228add017a4c9180e1e3968a26dedb4c"
"davidmoten/rtree2,7da3d606a192321217f6b780b6ab4fdcd8e3e1ed"
"dperezcabrera/jpoker,e771da71c3c5dc25b99355e41491933e78732e3e"
"eightbitjim/cassette-nibbler,788a04b49fe3d4c0905bd26109994d4952ad5db2"
"ElectronicChartCentre/java-vector-tile,f564aa95050f89e97aad4a0e93d7a9fbce3fcd42"
"f4b6a3/uuid-creator,f9e6e6d02ecc8dac16a56e4fab1bd24caec8171c"
"flipkart-incubator/databuilderframework,d739c964a4dda5fa212a5c52da61bc39d62ebe3a"
"fraunhoferfokus/Fuzzino,75d20f05db8dfbfe035a6df0b9eb7c88703886fc"
"fusion-jena/JaroWinklerSimilarity,03266936fa5350724979d78fef4213a20189ed0a"
"ghaffarian/progex,b8c75255305ba45dbcf7d895f81f415375edcd5e"
"Grundlefleck/ASM-NonClassloadingExtensions,8eb992f35817b2ef884a8dcaa502f829d85e5f90"
"hlavki/jlemmagen,43f7c636811a1f7fea7ae7db403ec6f3ec60e9b7"
"houbb/sensitive-word,344edf54f635c24e036dff4862d19a52603347c7"
"huaban/jieba-analysis,e46e44ba2c7b8534a9b489801f4ce0d38378ad1a"
"indeedeng/vowpal-wabbit-java,3a9a92ac11a69d265656806e84bc9c05d138ef88"
"jahlborn/jackcess,22bf8a8642c84fc500f5c66ef59de1f7211f93a3"
"kapoorlabs/kiara,40d11fb7e8d295c374f63d0e3b83d553d5374736"
"lexburner/consistent-hash-algorithm,a8e712fee24a1982f263d2f58ec770bfe34ac7e8"
"MezereonXP/AnomalyDetectTool,03db9e457cb9d1866c82c5d24618fbabcbdf48a8"
"mocnik-science/geogrid,702f29dffa36d82edf9744a79400a63fa7dde4db"
"myui/btree4j,4688aee221eaf2cf8972556a35cd6c49278ef2e0"
"renfei/ik-analyzer,ce4e534d99528270d96639230275a81f4df7e118"
"sbesada/java.math.expression.parser,cc92f58f6074b21cf6f5d4056b7f7cc5168f50af"
"solita/functional-utils,bf42b0192232c06ae6c50725c352cecca844b3f4"
"StarlangSoftware/TurkishPropBank,d99aae1239f782b42b077ce8e1a2b7e8e6ac716f"
"StarlangSoftware/TurkishSentiNet,636ab8932a35d78033e8e501221c386521a8cbb3"
"Sweetiee-yi/Jaba,6c5e46516fe63265c2d414ab94f52fe349ac1ebf"
"wiqer/ef-redis,bf067469f6f632b7b1cb1c17bd1377d1d6784328"
"zhoujianling/PointCloudUtilities,300e156f74278522d7fd7edec7ad4ce0307da622"
"dakusui/jcunit,5e081ae71f7e1ab8326aed77612a97c983c9dc06"
"finmath/finmath-lib,ad5d22e93e335cd88c95f8f2d7ba6336e3947e68"
"StarlangSoftware/TurkishDeasciifier,982c11d344788ed572a392a944a73993f83d5982"
"StarlangSoftware/TurkishSpellChecker,0b81eabd080b1a12fc94d08b49b7a094785a9601"
"spullara/java-future-jdk8,5925719802af19ccc6602651fc243b2ff3726b4b"
"FasterXML/jackson-core,de2c7328504c0cc1626bd0458ecd6115cf090df2"
"cocolian/cocolian-nlp,b82e28238261b12180cdbae11097e320824d87bb"
"lukfor/pgs-calc,27fbf7f069e8fded26262094e87fe9d0c6ad6a16"
"ngallagher/simplexml,01d47a6561bd5f7654b414591f8f02c66d316ab4"
"StarlangSoftware/TurkishMorphologicalDisambiguation,bf8dbc2cd835c67178eb896939ad1009b6743486"
"StarlangSoftware/TurkishWordNet,8caa11d2c121d135a5dc1cdd4ea848167b0fad00"
"stanfordnlp/CoreNLP,3499d27e615c35702f23948e886a7389b5695c33"
"orientechnologies/orientdb-jdbc,1cd2542848bfe411eafda3010a5a79ed9780de3e"
"santanusinha/json-rules,17b9ad528618949d1f87831af1b166f23e98fcdf"
"orientechnologies/orientdb-etl,a1c2ee119278c3f97cf6819130e281af21397f21"
)

for entry in "${projects[@]}"; do
    repo="${entry%%,*}"
    commit="${entry##*,}"
    project_name="${repo##*/}"

    export PATH=$(pwd)/sandbox-valg-rq3/home/Valg/apache-maven/bin:$(pwd)/sandbox-valg-rq3/usr/lib/jvm/java-8-openjdk/bin:$(pwd)/sandbox-valg-rq3/home/Valg/aspectj-1.9.7/bin:$PATH
    export CLASSPATH=$(pwd)/sandbox-valg-rq3/home/Valg/aspectj-1.9.7/lib/aspectjtools.jar:$(pwd)/sandbox-valg-rq3/home/Valg/aspectj-1.9.7/lib/aspectjrt.jar:$(pwd)/sandbox-valg-rq3/home/Valg/aspectj-1.9.7/lib/aspectjweaver.jar

    output_dir="output-$project_name"
    if ! $APPTAINER_CMD "$CONTAINER_PATHS" bash -c "cd $SCRIPT_PATH && env PATH=$PATH CLASSPATH=$CLASSPATH bash collect_traces.sh $repo $commit $output_dir"; then
    	echo "collect_traces.sh failed for $project_name ($repo)" >> run_valg_rq3.log
    	continue
    fi

    mkdir -p "$SCRIPT_PATH/$output_dir/trajectories"
    mkdir -p "$SCRIPT_PATH/$output_dir/time-series"
    mkdir -p "$SCRIPT_PATH/$output_dir/rq3"

    mv "$SCRIPT_PATH/$output_dir"/project/trajectories-* "$SCRIPT_PATH/$output_dir/trajectories"
    mv "$SCRIPT_PATH/$output_dir"/project/time-series-* "$SCRIPT_PATH/$output_dir/time-series"

    for traj_file in "$SCRIPT_PATH/$output_dir/trajectories"/trajectories-*; do
        base_id=$(basename "$traj_file" | sed 's/trajectories-//')
        ts_file="$SCRIPT_PATH/$output_dir/time-series/time-series-$base_id"
        out_file="$SCRIPT_PATH/$output_dir/rq3/$base_id.txt"

        python3 - <<PYTHON_EOF
import re

ts_dict = {}
with open("$ts_file") as f:
    last_loc = None
    for line in f:
        line = line.strip()
        if not line:
            continue
        if '@' in line and '=>' not in line:
            last_loc = line
            continue
        if '=>' in line and last_loc:
            seq = line.split('=>',1)[1].strip()[1:-1]
            ts_vals = []
            for item in seq.split(','):
                item = item.strip()
                if 'x' in item:
                    v, n = item.split('x')
                    ts_vals.extend([int(v)]*int(n))
                else:
                    ts_vals.append(int(item))
            ts_dict[last_loc.replace('Monitor','')] = ts_vals
            last_loc = None

traj_dict = {}
with open("$traj_file") as f:
    last_loc = None
    for line in f:
        line = line.strip()
        if not line:
            continue
        if '@' in line and '=>' not in line:
            last_loc = line
            continue
        if '=>' in line and last_loc:
            actions_list = re.findall(r'<(\d+): A=([^,]+),', line)
            traj_dict[last_loc] = actions_list
            last_loc = None

with open("$out_file",'w') as out:
    for loc, actions_list in traj_dict.items():
        ts_vals = ts_dict.get(loc, [])
        stepped = 0
        redundant = 0
        for idx_str, act in actions_list:
            idx = int(idx_str)
            if idx >= len(ts_vals):
                continue
            val = ts_vals[idx]
            if act == 'create':
                if val == 1:
                    stepped += 1
                else:
                    redundant += 1
        uniq = sum(1 for v in ts_vals if v==1)
        out.write(f"{loc}: {uniq} Unique Traces, {stepped} Preserved, {redundant} Redundant Traces\n")
PYTHON_EOF
    done

    mv "$SCRIPT_PATH/$output_dir/rq3" "$RESULTS_DIR/rq3-$project_name"

    tar -czf "$OUTPUT_DIR/$output_dir.tar.gz" -C "$SCRIPT_PATH" "$output_dir"
    rm -rf "$SCRIPT_PATH/$output_dir"
done
