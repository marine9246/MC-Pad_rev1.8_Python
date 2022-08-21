
#include "mbed.h"
#define  N446RE
//#define  F401RE

char soft_rev[] = "For MC-Pad rev1.8";

BusOut      M0_out(D5, D4, D3, D2);//Out4/3/2/1 左から0bit目
BusOut      M1_out(PB_1, PB_15, PB_14, PB_13);//
BusOut      zero_out(D4, D5, D2, D3, PB_13, PB_14, PB_15, PB_1/*,D6,D7,D8,D9,D10,D12*/);//モータ出力ポートを全て記載
PwmOut      pwm_1(D7);//Out1 PWM1/1 PA8 TIM1_CH1
PwmOut      pwm_2(D8);     //PWM1/2 PA9 TIM1_Ch2
PwmOut      pwm_3(D9);     //PWM3/2 PC7 TIM3_CH3
PwmOut      pwm_4(D12);    //PWM3/1 PA6 TIM3_CH1
DigitalIn Dtvrs_1(PC_8);
DigitalIn Dtvrs_2(PC_6);
DigitalIn Dtvrs_3(PC_5);
DigitalIn Dtvrs_4(PA_12);
DigitalOut  RSon_1(D6);
DigitalOut  RSon_2(D10);
DigitalOut  Trg(D11);
InterruptIn mybutton(USER_BUTTON);
DigitalIn stop_but(PA_14,PullDown);
Serial      pc(USBTX, USBRX);

AnalogIn piout(PC_4);//PI出力読み取り
DigitalOut  pictl(D15);//PILED ON/OFF

PwmOut      pwm_led(PA_15);//pwmライト点灯用 PWM

Timer pulse_time;
Timer section_time;
Timer button_time;

#ifdef N446RE
AnalogOut dac_out(A2);
AnalogIn adc_in(A0);
AnalogOut   dac_vref(D13);
DigitalOut  LED(PC_3);
#endif

#ifdef F401RE
DigitalOut  LED(D13);
#endif

/////パルス設定//////////////////////////////////////////////////////
int chop_period  = 488-8;  //チョッピング周期[us](処理の関係で小さく設定する)

//パルス1（Pulse 0/1）
int P1w_1     = 0;  //正転P1パルス幅[us]
int P1w_2     = 1000;  //正転P1パルス幅[us]
int P1w_3     = 2000;  //正転P1パルス幅[us]
int P1w_4     = 2000;  //正転P1パルス幅[us]
int P1w_5     = 0;  //正転P1パルス幅[us]
int P1w_6     = 0;  //正転P1パルス幅[us]
int P1n_1     = 1;    //正転P1パルス本数(パルス幅488未満で有効)
int P1n_2     = 1;    //正転P1パルス本数(パルスy幅488未満で有効)
int P1n_3     = 1;    //正転aP1パルス本数(パルス幅488未満で有効)
int P1n_4     = 1;    //正転P1パルス本数(パルス幅488未満で有効)
int P1n_5     = 1;    //正転aP1パルス本数(パルス幅488未満で有効)
int P1n_6     = 1;    //正転P1パルス本数(パルス幅488未満で有効)

//パルス2（Pulse 2/3）
int P2w_1     = 0;  //正転P1パルス幅[us]
int P2w_2     = 1000;  //正転P1パルス幅[us]
int P2w_3     = 2000;  //正転P1パルス幅[us]
int P2w_4     = 2000;  //正転P1パルス幅[us]
int P2w_5     = 0;  //正転P1パルス幅[us]
int P2w_6     = 0;  //正転P1パルス幅[us]
int P2n_1     = 1;    //正転P1パルス本数(パルス幅488未満で有効)
int P2n_2     = 1;    //正転P1パルス本数(パルスy幅488未満で有効)
int P2n_3     = 1;    //正転aP1パルス本数(パルス幅488未満で有効)
int P2n_4     = 1;    //正転P1パルス本数(パルス幅488未満で有効)
int P2n_5     = 1;    //正転aP1パルス本数(パルス幅488未満で有効)
int P2n_6     = 1;    //正転P1パルス本数(パルス幅488未満で有効)

//パルス3（Pulse 4）
int P4w_1     = 1500;  //正転P1パルス幅[us]
int P4w_2     = 0;  //正転P1パルス幅[us]
int P4w_3     = 0;  //正転P1パルス幅[us]
int P4w_4     = 0;  //正転P1パルス幅[us]
int P4w_5     = 0;  //正転P1パルス幅[us]
int P4w_6     = 0;  //正転P1パルス幅[us]
int P4n_1     = 1;    //正転P1パルス本数(パルス幅488未満で有効)
int P4n_2     = 1;    //正転P1パルス本数(パルス幅488未満で有効)
int P4n_3     = 1;    //正転P1パルス本数(パルス幅488未満で有効)
int P4n_4     = 1;    //正転P1パルス本数(パルス幅488未満で有効)
int P4n_5     = 1;    //正転P1パルス本数(パルス幅488未満で有効)
int P4n_6     = 1;    //正転P1パルス本数(パルス幅488未満で有効)
//パルス3（Pulse 5）
int P5w_1     = 630;  //正転P1パルス幅[us]
int P5w_2     = 630;  //正転P1パルス幅[us]
int P5w_3     = 1260;  //正転P1パルス幅[us]
int P5w_4     = 0;  //正転P1パルス幅[us]
int P5w_5     = 0;  //正転P1パルス幅[us]
int P5w_6     = 0;  //正転P1パルス幅[us]
int P5n_1     = 1;    //正転P1パルス本数(パルス幅488未満で有効)
int P5n_2     = 1;    //正転P1パルス本数(パルス幅488未満で有効)
int P5n_3     = 1;    //正転P1パルス本数(パルス幅488未満で有効)
int P5n_4     = 1;    //正転P1パルス本数(パルス幅488未満で有効)
int P5n_5     = 1;    //正転P1パルス本数(パルス幅488未満で有効)
int P5n_6     = 1;    //正転P1パルス本数(パルス幅488未満で有効)
//Pr（Pulse 6）
int P6w_1     = 0;  //正転P1パルス幅[us]
int P6w_2     = 0;  //正転P1パルス幅[us]
int P6w_3     = 0;  //正転P1パルス幅[us]
int P6w_4     = 366;  //正転P1パルス幅[us]
int P6w_5     = 0;  //正転P1パルス幅[us]
int P6w_6     = 10000;  //正転P1パルス幅[us]
int P6n_1     = 1;    //正転P1パルス本数(パルス幅488未満で有効)
int P6n_2     = 1;    //正転P1パルス本数(パルスy幅488未満で有効)
int P6n_3     = 1;    //正転aP1パルス本数(パルス幅488未満で有効)
int P6n_4     = 10;    //正転P1パルス本数(パルス幅488未満で有効)
int P6n_5     = 1;    //正転aP1パルス本数(パルス幅488未満で有効)
int P6n_6     = 1;    //正転P1パルス本数(パルス幅488未満で有効)
//Pe
int Pe_width  = 488;   //Peパルス長さ
int Pe_wait   = 6000; //Pe後のWait時間

////////////////////////////////00/////////////////////////////////////
///7-4bit 検出ON設定、3-0bit パルス設定　3bitがOut1
int pattern[9][13]   = {   
            {0x0,0x8,0xA,0x2,0x6,0x40,0x0,0x4,0x5,0x81,0x9,0x80,0x0},//正転パルス1
            {0x0,0x1,0x5,0x4,0x6,0x20,0x0,0x2,0xA,0x8,0x9,0x10,0x0},//逆転パルス1
            {0x0,0x8,0xA,0x2,0x6,0x40,0x0,0x4,0x5,0x81,0x9,0x80,0x0},//正転パルス2
            {0x0,0x1,0x5,0x4,0x6,0x20,0x0,0x2,0xA,0x8,0x9,0x10,0x0},//逆転パルス2
            {0x0,0x8,0xA,0x2,0x6,0x40,0x0,0x4,0x5,0x81,0x9,0x80,0x0},//正転パルス3                  
            {0x0,0x1,0x5,0x4,0x6,0x20,0x0,0x2,0xA,0x8,0x9,0x10,0x0},//逆転パルス3
            {0x0,0x1,0x5,0x4,0x6,0x20,0x0,0x2,0xA,0x8,0x9,0x10,0x0},//Pr
            };

int pwidth[9][13] = { //パルス長さ
    {0, P1w_1,P1w_2,P1w_3,P1w_4,P1w_5,P1w_6,  P1w_1,P1w_2,P1w_3,P1w_4,P1w_5,P1w_6},
    {0, P1w_1,P1w_2,P1w_3,P1w_4,P1w_5,P1w_6,  P1w_1,P1w_2,P1w_3,P1w_4,P1w_5,P1w_6},
    {0, P2w_1,P2w_2,P2w_3,P2w_4,P2w_5,P2w_6,  P2w_1,P2w_2,P2w_3,P2w_4,P2w_5,P2w_6},
    {0, P2w_1,P2w_2,P2w_3,P2w_4,P2w_5,P2w_6,  P2w_1,P2w_2,P2w_3,P2w_4,P2w_5,P2w_6},
    {0, P4w_1,P4w_2,P4w_3,P4w_4,P4w_5,P4w_6,  P4w_1,P4w_2,P4w_3,P4w_4,P4w_5,P4w_6},
    {0, P5w_1,P5w_2,P5w_3,P5w_4,P5w_5,P5w_6,  P5w_1,P5w_2,P5w_3,P5w_4,P5w_5,P5w_6},
    {0, P6w_1,P6w_2,P6w_3,P6w_4,P6w_5,P6w_6,  P6w_1,P6w_2,P6w_3,P6w_4,P6w_5,P6w_6}
    };

char pcnt[9][13] = { //パルス本数
    {0, P1n_1,P1n_2,P1n_3,P1n_4,P1n_5,P1n_6,  P1n_1,P1n_2,P1n_3,P1n_4,P1n_5,P1n_6},
    {0, P1n_1,P1n_2,P1n_3,P1n_4,P1n_5,P1n_6,  P1n_1,P1n_2,P1n_3,P1n_4,P1n_5,P1n_6},
    {0, P2n_1,P2n_2,P2n_3,P2n_4,P2n_5,P2n_6,  P2n_1,P2n_2,P2n_3,P2n_4,P2n_5,P2n_6},
    {0, P2n_1,P2n_2,P2n_3,P2n_4,P2n_5,P2n_6,  P2n_1,P2n_2,P2n_3,P2n_4,P2n_5,P2n_6},
    {0, P4n_1,P4n_2,P4n_3,P4n_4,P4n_5,P4n_6,  P4n_1,P4n_2,P4n_3,P4n_4,P4n_5,P4n_6},
    {0, P5n_1,P5n_2,P5n_3,P5n_4,P5n_5,P5n_6,  P5n_1,P5n_2,P5n_3,P5n_4,P5n_5,P5n_6},    
    {0, P6n_1,P6n_2,P6n_3,P6n_4,P6n_5,P6n_6,  P6n_1,P6n_2,P6n_3,P6n_4,P6n_5,P6n_6}
    };

int pseq[3][21][7]={ //パルスシーケンス設定
    {
        {0,1,0,60,5000,0b011000001},
        {0,1,0,60,5000,0b011000001},
        {0,1,0,60,5000,0b011000001},
        {0,1,0,60,5000,0b011000001},
        {0,1,0,60,5000,0b011000001},
        {0,0,0,0,5000,0b011000001},//月/
    },
    {
        {0,0,60,0,10000,0b001000001},
        {1,0,20,0,10000,0b001000001},
        {0,0,20,0,10000,0b001000001},
        {1,0,60,0,10000,0b011000001},
        {1,0,100,100,5000,0b011000001},
        {0,1,100,100,5000,0b011000001},
        {0,1,0,30,6250,0b001000001},
        {0,0,0,30,6250,0b001000001},
        {0,1,0,30,6250,0b001000001},
        {1,0,0,30,6250,0b001000001},
        {0,0,20,0,10000,0b001000001},
        {1,0,20,0,10000,0b001000001},
        {0,0,0,0,10000,0b001000001},//ミソサザイ動作*/
    },
    {        
        {1,1,60,60,10000,0b011000001},
        {0,0,60,0,5000,0b011000001},
        {1,1,60,60,10000,0b011000001},
        {0,0,60,0,5000,0b011000001},
        {1,1,60,60,10000,0b011000001},
        {0,0,60,0,5000,0b011000001},
        {1,1,60,60,10000,0b011000001},
    }    
    };

float pseq_vm[21][1] ={//シーケンス用電圧設定
    {3.0},{3.0},{3.0},{3.0},{3.0},{3.0},{3.0},{3.0},{3.0},{3.0},
    {3.0},{3.0},{3.0},{3.0},{3.0},{3.0},{3.0},{3.0},{3.0},{3.0},
    };

int vrs_time[4][20];//vrsタイミング保存
#ifdef N446RE
int vrs_result[360][40];//Vrs結果保存　360stepまで
int vrs_cnt[4]={0,0,0,0};
#endif

float Vset_out=0; //現在出力しているの電圧値
float Vset = 0;                 //Vmotoer出力電圧設定、これの1/2がDacの出力電圧
float Diff = 0;                 //DAC出力*2とADC入力の差異
float pwm_func[4]={pwm_1,pwm_2,pwm_3,pwm_4};
float pwm_duty = 0.10;
float pwm_period = 0.0005;
float pwm2_duty = 0.10;
float pwm2_period = 0.0005; 

int state[2]={1,1}; //M0M1の極性記憶
char mode_stat = 0;//demo動作でモード記憶
char button_state=0;
char seq_number = 0;
char int_act = 0;//デモ動作時にwaitを入れない場合に1

int pw_adjnum =5; //パルス長さ調整
int wait_adjnum = 0;//Wait長さ調整      
int pulse_setnum =0; //出力パルス     
//int M0_state = 1;      //スタートパルス状態　使ってない？
//int M1_state = 1;
int M0_posi = 0; //基準位置からのステップ数　AC後は
int M1_posi = 0; //
int statemax = 12;   //パルス種類
int state_Pe = 0;    //Peパルスのstate
int select = 0;    //パルス種類選択　使ってない？
int anystep_cnt = 60;
int pulse_mode; //パルスオプションの有効無効を記憶
char pcnt_set = 1;
//int wait_time = 2000; //パルス間Wait（無励磁時間msec)
int full_step = 360; //1周のステップ数
int pulse_period=5000;//パルス出力周期[us]

int pr_en =0;

//Vref設定
float vref_value =1;

//フォトインタラプタ関連
int pivth = 3300;
int pi_pulse =7;
int pi_detstep = 1;//piで反応するステップ数-1
//int pi_wait = 2000;
int pi_period = 5000;//パルス出力周期[us]
float pi_vset =3;
int pi_mode = 0;
char pi_judg = 0;//駆動中判定の有無
int pi_offset = 0;
int pi_inpulse = 0;

//停止処理
char stop_bit = 0;

void Dac_out_process(float vout)
{
#ifdef N446RE
    Vset_out = vout;                                 //Dac出力値をVset_outに保存
    float dac_data = (vout/2.0f)/3.3f;          //dac_data変換
    dac_out = dac_data+Diff;                    //Dac出力
    wait(0.2);                                  //2020/6/24 電圧安定時間100msだったためWait時間変更 1sec→0.2sec
#endif
}
//-------　これがオフセット電圧の補正処理です。---
//  DAC出力をAMPで2倍する際の誤差をADCで測定し補正
//　±500mv以内なら補正するが、それ以外は補正値0
//------------------------------------------------
void Adj_dac(void)
{
#ifdef N446RE
    Vset = 2.0f;                //2V出力想定
    Dac_out_process(Vset);
    wait(0.1);                  //とりあえず、安定時間として100msec待つ

    float adc_data = adc_in;            //ADC入力
    Diff = (Vset/3.3f-adc_data)/2.0f;   //DAC出力とADC入力の差異,外部で2倍しているので差異も2倍されている
    
    if ((Diff > (0.5f/2.0f/3.3f)) || (Diff < -(0.5f/2.0f/3.3f)))   //±500mVより大なら補正しない
        Diff = 0.0f;
#endif
}

//rev0.9追加
//Vrsタイミング記録
void vrs_rec(int vrs_ch){
#ifdef N446RE
    int readtime = pulse_time.read_us();
    if(vrs_cnt[vrs_ch]==0){//1本目は必ず記録
        vrs_time[vrs_ch][vrs_cnt[vrs_ch]] = readtime;
        vrs_cnt[vrs_ch] ++;
    }
    else{//2本目以降はSPK周期以上だったら記録、最大20本まで
        int difftime = readtime -vrs_time[vrs_ch][vrs_cnt[vrs_ch]-1];
        if(difftime+20 > pwm_period*1000000 && vrs_cnt[vrs_ch]<20){
            vrs_time[vrs_ch][vrs_cnt[vrs_ch]] = readtime;
            vrs_cnt[vrs_ch] ++;
        }
    }
#endif
}

//Vrs結果保存 ※最初のステップが0行目
void vrs_save(int M0_cnt){
#ifdef N446RE
    if(M0_cnt<360){
        int data_cnt =0;
        for(int ch=0; ch<4; ch++){
            if(data_cnt>39){break;}
            vrs_result[M0_cnt][data_cnt]=ch+1;//検出ch記録
            data_cnt++;
            vrs_cnt[ch]=0;//vrs_cntの初期化
            for(int vcnt=0; vcnt<20; vcnt++){
                if(vrs_time[ch][vcnt]==0){break;}
                if(data_cnt>39){break;}
                vrs_result[M0_cnt][data_cnt]=vrs_time[ch][vcnt];//検出時間記録
                data_cnt++;
                vrs_time[ch][vcnt] = 0;//vrs_timeの初期化                                
            }
        }
    }
#endif
}

//Vrs結果プリント
void vrs_print(){
#ifdef N446RE
    pc.printf(",");
    for(int i =0; i<360; i++){
        for(int n=0; n<40; n++){
            if(vrs_result[i][n]==0){break;}
            pc.printf("%d,",vrs_result[i][n]);
            vrs_result[i][n]=0;
        }
    }
#endif
}

//パルス中のフォト出力検出 最大値
void piout_rec(){
    int pi_adc;
    pi_adc = (int)3300*piout;
    if(pi_adc > pi_inpulse){
        pi_inpulse = pi_adc;
    }
}

void output_step(int mt_type, int mt_dr ,int mode_en) //（M0 or M1/パルスNo/パルスOption)
{    
    pcnt_set = pcnt[mt_dr][state[mt_type]];//パルス本数セット
    if(pwidth[mt_dr][state[mt_type]]==0){
        pcnt_set = 0;//パルス時間がゼロだったら本数もゼロにする debug指摘 No.10/11対応
    }
    if((mode_en>>2)&1==1){ //pwm設定で数10usかかるためvrs有効時のみ
        pwm_1.period(pwm_period);//pwm周期設定
        pwm_2.period(pwm_period);
        pwm_3.period(pwm_period);
        pwm_4.period(pwm_period);
    }

    int i = 0;

    if(mt_dr==6 || mt_dr==2 || mt_dr==3){//Prと補正駆動時は極性更新しない
        state[mt_type]=state[mt_type]+6;
        if(state[mt_type]>12){state[mt_type]=1;} 
    }

    if((mode_en>>4)&1==1 && mt_dr <2){//4bit目が1だったらPe出力 Prの時はなし　//Pe出力部
        switch(mt_type){
            case 0: M0_out = pattern[mt_dr][state_Pe+state[mt_type]-1];break;
            case 1: M1_out = pattern[mt_dr][state_Pe+state[mt_type]-1];break;
            }
        wait_us(Pe_width);
        zero_out =  0;
        wait_us(Pe_wait);      
    }
    pulse_time.reset();//パルス開始からのタイマ
    //if((mode_en>>0)&1==1 && mt_type==0){//0bit目が1だったらトリガ出力
    //    Trg = 1; //以前トグルとしていたのはトリガが出る極性を固定するため
    //}
    pi_inpulse = 0;
    while(i<6){
        if(stop_but==1){i=10;}//stop_but押されたらパルス強制停止
        /*
        if(pcnt[mt_dr][state[mt_type]]>1 && pwidth[mt_dr][state[mt_type]]<=chop_period){
            //パルス時間がチョッピング周期より短く、本数が1より大きい時はチョッピングパルス
            zero_out =  0;//チョッピングパルス出力時は最初ゼロ出力
            wait_us(chop_period-pwidth[mt_dr][state[mt_type]]);
        }
        */
        section_time.reset();//セクションタイマリセット
        if((mode_en>>0)&1==1 && mt_type==0 && i == 0){//0bit目が1だったらトリガ出力
            Trg = 1; //トリガ出力からパルス出力までの間に処理を入れないように移動
        }

        if(pwidth[mt_dr][state[mt_type]]>0){//パルス出力
            switch(mt_type){
                case 0: M0_out = pattern[mt_dr][state[0]];break;
                case 1: M1_out = pattern[mt_dr][state[1]];break;
            }
            if((mode_en>>2)&1==1){//2bit目が1だったらVrs検出あり
                if((pattern[mt_dr][state[0]] & 0b11000000) > 0){RSon_1=1;}
                else{RSon_1=0;}
                if((pattern[mt_dr][state[0]] & 0b00110000) > 0){RSon_2=1;}
                else{RSon_2=0;}
                if((pattern[mt_dr][state[0]]>>7)&1 == 1){pwm_1=pwm_duty;}
                else{pwm_1=0;}
                if((pattern[mt_dr][state[0]]>>6)&1 == 1){pwm_2=pwm_duty;}
                else{pwm_2=0;}
                if((pattern[mt_dr][state[0]]>>5)&1 == 1){pwm_3=pwm_duty;}
                else{pwm_3=0;}
                if((pattern[mt_dr][state[0]]>>4)&1 == 1){pwm_4=pwm_duty;}
                else{pwm_4=0;}               
            }
            switch(mt_dr){
                case 7://フォト検出用パルスだったら
                case 8:
                    while (section_time.read_us()<pwidth[mt_dr][state[mt_type]]){//Rev1.5 パルス中のpiadc読み取り
                        piout_rec();
                    }
                    if(pcnt[mt_dr][state[mt_type]]>1 && pwidth[mt_dr][state[mt_type]]<=chop_period){
                        //パルス時間がチョッピング周期より短く、本数が1より大きい時はチョッピングパルス
                        zero_out =  0;
                        while (section_time.read_us()<chop_period){
                            piout_rec();
                        } 
                    }                    
                    break;
                default:
                    while (section_time.read_us()<pwidth[mt_dr][state[mt_type]]){//Rev0.9 waitからtimer比較に変更。time読み取りループだけだと2-3us
                        if(pwm_1 > 0 && Dtvrs_1 == 1){vrs_rec(0);}
                        if(pwm_2 > 0 && Dtvrs_2 == 1){vrs_rec(1);}
                        if(pwm_3 > 0 && Dtvrs_3 == 1){vrs_rec(2);}
                        if(pwm_4 > 0 && Dtvrs_4 == 1){vrs_rec(3);}
                    }

                    if(pcnt[mt_dr][state[mt_type]]>1 && pwidth[mt_dr][state[mt_type]]<=chop_period){
                        //パルス時間がチョッピング周期より短く、本数が1より大きい時はチョッピングパルス
                        zero_out =  0;
                        while (section_time.read_us()<chop_period){
                            if(pwm_1 > 0 && Dtvrs_1 == 1){vrs_rec(0);}
                            if(pwm_2 > 0 && Dtvrs_2 == 1){vrs_rec(1);}
                            if(pwm_3 > 0 && Dtvrs_3 == 1){vrs_rec(2);}
                            if(pwm_4 > 0 && Dtvrs_4 == 1){vrs_rec(3);}                    
                        } 
                    }
                    break;
            }
            Trg = 0;
        }

        if(pcnt_set!=0){//pcntが0だったらwait出力や減算しない   debug指摘 No.8対応                
            pcnt_set --;
        }        
        
        if(pcnt_set==0){//極性更新
            state[mt_type]++;
            if(state[mt_type]>statemax){state[mt_type]=1;} 
            pcnt_set = pcnt[mt_dr][state[mt_type]];
            i++;
        }
    }
    //zero_out =  0;
    //pwm_1=pwm_2=pwm_3=pwm_4=0;
    //RSon_1 = RSon_2 = 0;
}

//パルス生成サブルーチン
//(M0_Pulse,M1_Pulse,M0_step,M1_step,wait,option,Vm)
void rotate(int M0_dr, int M1_dr, 
            int M0_steps ,int M1_steps, 
            float inttime,int mode_en,//mode_en:0Triger/1極性反転/2Vrs/3補正P/4Pe/5Wait/6終Pr/7Wait2
            float Vm)
{   
#ifdef N446RE
    dac_vref = vref_value;
#endif

    pulse_time.start();//パルス開始からのタイマ
    section_time.start();
    vrs_time[0][0]=0;//

    if(Vm!=Vset_out){Dac_out_process(Vm);} //電圧変更時は電圧設定変更

    int  M0_cnt = M0_steps;   //stepカウント
    int  M1_cnt = M1_steps;   //stepカウント

    if(inttime>wait_adjnum){inttime=inttime-wait_adjnum;}//Wate時間補正

    if((mode_en>>4)&1==1){//4bit目が1だったら 初めの駆動パルスと同じPeパルスをセット
        int n = 1;
        while(n<7){
            if(pwidth[M0_dr][n]==0){n++;}
            else{state_Pe = n;//初めの駆動パルスNo
                n=7;
            }
        }
    }
    if(M0_dr==6 || M0_dr==2 || M0_dr==3){;}//Prと補正駆動時は逆極性パルスにしない
    else if((mode_en>>1)&1==1 && M0_cnt > 0){//極性反転(1bit目)が1だったら　逆極性パルス
        state[0]=state[0]+6;
        if(state[0]>12){state[0]=1;}
    }

    if(M1_dr==6 || M1_dr==2 || M1_dr==3){;}//Prと補正駆動時は逆極性パルスにしない
    else if((mode_en>>1)&1==1 && M1_cnt > 0){//極性反転(1bit目)が1だったら　逆極性パルス
        state[1]=state[1]+6;
        if(state[1]>12){state[1]=1;}
    }            

    while(M0_cnt >0 || M1_cnt > 0){//パルス出力ループ。M0出力終了後にM1出力をcnt=0まで繰り返す
        if(int_act ==1 || stop_but==1){//stop_but押されたらカウントゼロにしてパルス出力停止
           M0_cnt=0;
           M1_cnt=0;
        }
        if(M0_cnt > 0){
            output_step(0,M0_dr,mode_en);
            if((mode_en>>3)&1==1){//3bit目が1だったら補正パルスあり
                output_step(0,M0_dr+2,mode_en & 0b111110);//補正パルスはトリガなし
            }
            M0_cnt--;
            switch(M0_dr){
                case 0:
                case 2:
                case 4:
                case 7:
                    M0_posi++;
                    if(M0_posi==full_step){M0_posi=0;}
                    break;
                case 1:
                case 3:
                case 5:
                case 8:
                    if(M0_posi==0){M0_posi=full_step;}
                    M0_posi--;
                    break;
            }
            if (M0_cnt == 0 && (mode_en>>6)&1==1){
                output_step(0,6,mode_en & 0b111110);//ステップ最後にPr
            }
        }
        //M0パルス終了処理
        zero_out =  0;
        if((mode_en>>2)&1==1){          
            RSon_1=RSon_2=0;
            pwm_1=pwm_2=pwm_3=pwm_4=0;
            vrs_save(M0_steps-(M0_cnt+1));}//2bit目が1だったらVrs検出結果保存

        if(M1_cnt > 0){
            output_step(1,M1_dr,mode_en);
            M1_cnt--;
            switch(M1_dr){
                case 0:
                case 2:
                    M1_posi++;
                    if(M1_posi==full_step){M1_posi=0;}
                    break;
                case 1:
                case 3:
                    if(M1_posi==0){M1_posi=full_step;}
                    M1_posi--;
                    break;
            }
            if (M1_cnt == 0 && (mode_en>>6)&1==1){
                output_step(1,6,mode_en & 0b111110);//ステップ最後にPr
            }            
        }
        //section_time.reset();//セクションタイマリセット
        /*
        if((mode_en>>3)&1==1){//3bit目が1だったら
            pwm_1.period(pwm2_period);
            pwm_2.period(pwm2_period);
            pwm_3.period(pwm2_period);
            pwm_4.period(pwm2_period);
            RSon_1=RSon_2=1;
            pwm_1=pwm_2=pwm_3=pwm_4=pwm2_duty; 
        }
        */
        zero_out =  0;//M1パルス終了処理

        //wait_us(inttime);
        //while (section_time.read_us()<inttime){}
        while (pulse_time.read_us()<inttime){
            if(M0_dr == 7 || M0_dr == 8 ){
                piout_rec();
            }
        }
        //pc.printf("%dV",pi_inpulse);
    }
    if(pulse_time.read_us() > inttime + 100){
        if(M0_dr != 6 && M0_dr != 2 && M0_dr != 3){
            float freq_done = 1/(float)pulse_time.read();
            pc.printf("al-f%dHz,",(int)freq_done);
        }
    }
   
    if((mode_en>>5)&1==1){//5bit目が1だったら
        wait(0.05);//50msec待つ
    }
    if((mode_en>>7)&1==1){//6bit目が1だったら
        wait(0.5);//500msec待つ
    }
    if((mode_en>>2)&1==1){vrs_print();}//2bit目が1だったらVrs検出結果プリント

    pulse_time.stop();//パルスタイマストップ
    section_time.stop();
    RSon_1=RSon_2=0;
    pwm_1=pwm_2=pwm_3=pwm_4=0;
#ifdef N446RE
    dac_vref = 0;
#endif
    Trg = 0;
    stop_bit = 0;
    __enable_irq(); // 許可
}

//Pulse幅調整
void Pw_adj(){
    int n = 0;
    while(n<7){
        int i = 0;
        while(i<12){//2020/6/26 パルス区間増加により増やした
            if(pwidth[n][i]>pw_adjnum){pwidth[n][i]=pwidth[n][i]-pw_adjnum;}
            i++;
        }
        n++;
    }
}


//zero位置へ移動
//(M0_Pulse,M1_Pulse,wait)
void Zero_posi(int M0_dr, int M1_dr, int inttime){
    __disable_irq();
    int M0_step2zero = 0;
    int M1_step2zero = 0;
    if(M0_posi >0 ){M0_step2zero = full_step-M0_posi;}
    if(M1_posi > 0){M1_step2zero = full_step-M1_posi;}

    rotate(M0_dr, M1_dr, M0_step2zero,M1_step2zero,inttime,0,Vset);
    M0_posi=0;
    M1_posi=0;
    wait(0.5);
    __enable_irq(); // 許可 
}

//M0を指定位置へ
//(M0_Pulse,M0_指定位置,wait)
void Goto_posi(int M0_dr,int offset, int inttime, float v_set){
    __disable_irq();
    int tag_posi;
    switch(M0_dr){
        case 1:
        case 3:
        case 5:
        case 8:
            tag_posi = offset;//CCWの時
            break;
        default:
            tag_posi = full_step - offset;//CWの時
            break;
    }
    int M0_step2posi = 0;
    if(M0_posi < tag_posi){
        M0_step2posi = tag_posi-M0_posi;
    }
    else if(M0_posi > tag_posi){
        M0_step2posi = full_step-M0_posi+tag_posi;
    }
    switch(M0_dr){//逆転の場合ステップ数調整
        case 1:
        case 3:
        case 5:
        case 8:
            M0_step2posi = full_step - M0_step2posi;
            break;
    }
    if (pi_mode ==1 && M0_step2posi > full_step/2){//pi検出モード=3
        int back_step = full_step-M0_step2posi+10;//check位置に行くときに最短方向に動く
        M0_step2posi = 10;
        rotate(pi_pulse^0b1111,0,back_step,0,pi_period,0,pi_vset);
    }
    rotate(M0_dr, 0, M0_step2posi,0,inttime,0,v_set);
    //M0_posi = tag_posi;
    __enable_irq(); // 許可 
}

void Main_menu(){
    //pc.printf("1:M0 position\n");
    //pc.printf("2:M1 position\n");
    pc.printf("0:zero_set\n");    
    pc.printf("1:pulse_set\n");
    pc.printf("2:pulse_period_set\n");
    pc.printf("3:pulse_width_set\n");
    pc.printf("4:pulse_num_set\n");
    pc.printf("5:sequence_set\n");
    pc.printf("6:pulsemode_set\n");
    pc.printf("7:anystep_set\n");
    pc.printf("8:pe_set\n");
    pc.printf("9:sequence_run\n");
    pc.printf("-:Spk_set\n");  
    pc.printf("^:Voltage_set\n");
    pc.printf("p:P-train_set\n");
    pc.printf("o:Vref set\n");
    pc.printf("z:1step_CW/--\n");
    pc.printf("x:1step_CCW/--\n"); 
    //pc.printf("c:1step_--/CW\n");
    pc.printf("v:rev_chek\n");
    pc.printf("b:anystep_CW/--\n");
    pc.printf("n:anystep_CCW/--\n"); 
    pc.printf("a:360step_CW/--\n");
    pc.printf("s:360step_CCW/--\n"); 
    pc.printf("d:360step_--/CW\n");
    pc.printf("f:360step_--/CCW\n");
    pc.printf("q:Pr_Pr/--\n");
    pc.printf("w:PI Vth set\n");
    pc.printf("e:PI posiset\n");
    pc.printf("r:PI posicheck\n");
    pc.printf("t:PI pulseset\n");        
    //pc.printf("q:360step_CW/CW\n");
    //pc.printf("w:360step_CCW/CCW\n");
    //pc.printf("e:360step_CW/CCW\n");
    //pc.printf("r:360step_CCW/CW\n");
    //pc.printf("h:Reduce-wait_CW/--\n");
    //pc.printf("j:Reduce-wait_CCW/--\n"); 
    //pc.printf("k:Reduce-wait_--/CW\n");
    //pc.printf("l:Reduce-wait_--/CCW\n");
    //pc.printf("p:305Hz vs 31Hz\n");
         
}

int pc_input_3digit_Re(){
    double PC_Input[3];
    PC_Input[0] = pc.getc()-48;//参考URL http://www.mbed-nucleo.net/article/442397444.html
    pc.putc(PC_Input[0]+48);
    PC_Input[1] = pc.getc()-48;
    pc.putc(PC_Input[1]+48);
    PC_Input[2] = pc.getc()-48;
    pc.putc(PC_Input[2]+48);
    int Trip_digits = PC_Input[0]*100+PC_Input[1]*10+PC_Input[2]; 
    return Trip_digits;
    }

void getline(char line[],int lim){//enter(CR)受信まで受信
    int c,i;
    for (i = 0; i < lim - 1 && (c = getchar()) != '\r'; ++i){
        if(c == '\b'){
            if(i>0){i=i-2;}
        }
        else{
            line[i] =c;
        }
        pc.putc(c);
    }
    if(i==0){
        line[i]=0;
        i++;
        pc.printf("0");
    }
    line[i] = '\0';
}

void pulse_set(){
    pc.printf("Pulse set 0 or 2,4\n");
    pc.printf("Pulse_set(1)=");
    pulse_setnum = pc.getc()-48;
    pc.putc(pulse_setnum+48);
    pc.printf(" select\n"); 
}

/*
void wait_time_set(){
    pc.printf("Wait_time(usec)=");
    char str[10];
    getline(str, 9);
    pc.printf("usec\n");
    wait_time = atoi(str);
    //printf("%d\n",wait_time);      
}
*/

void pulse_period_set(){
    pc.printf("Pulse_period(Hz)=");
    char str[10];
    getline(str, 9);
    pulse_period = (int)(1/atof(str)*1000000);  
    pc.printf("Hz %dus\n",pulse_period);  
}

void pulse_width_set(){
    pc.printf("Pulese(1)=");
    int psele = pc.getc()-48;
    pc.putc(psele+48);
    pc.printf(" "); 
    int i = 1;
    char str[10];
    pc.printf("Pwid=");
    while(i<7){
        getline(str, 9);
        int pwid_save = atoi(str);
        if(pwid_save>pw_adjnum){pwid_save=pwid_save-pw_adjnum;}
        pwidth[psele][i] = pwid_save;
        pwidth[psele][i+6] = pwid_save;
        pc.printf(" ");
        i++;
    }
    pc.printf("us\n");
}

void pulse_num_set(){
    pc.printf("Pulese(1)=");
    int psele = pc.getc()-48;
    pc.putc(psele+48);
    pc.printf(" "); 
    int i = 1;
    char str[10];
    pc.printf("Pnum=");
    while(i<7){
        getline(str, 6);
        pcnt[psele][i] = atoi(str);
        pcnt[psele][i+6] = atoi(str);
        pc.printf(" ");
        i++;
    }
    pc.printf("\n");
    //i=0;
    //while(i<10){
    //    pc.printf("%d\n",pcnt[psele][i]);
    //    i++;
    //}
}

void sequence_set(){
    int i = 0;
    char str[10];
    while(i<20){
        pc.printf("seq-%d ",i);
        int m =0;
        while(m<6){ //M0/M1パルス,M0/M1ステップ,wait[us],パルスオプション
            //pc.printf("prm%d set = ",m);
            getline(str, 10);
            pseq[seq_number][i][m] = atoi(str);
            pc.printf(" ");
            if(m==4){
                if(pseq[seq_number][i][m] != 0){
                    pseq[seq_number][i][m] = (int)(1/atof(str)*1000000);//周波数をusに変換
                }
            }
            //pc.printf(" %d" ,pseq[seq_number][i][m]);//入力check
            //pc.printf("\n");
            m++;
        }
       // pc.printf("prm%d set = ",m);
        getline(str, 10);
        pseq_vm[i][1] = atof(str);
        pc.printf(" ");
        //pc.printf(" %.1f",pseq_vm[i][1]);//入力check
        pc.printf("\n");
        if(pseq[seq_number][i][2] ==0 && pseq[seq_number][i][3] ==0){break;}//M0&M1step数がゼロだったら書込み終了
        i++;
    }
    
}

void mode_set(){
    pc.printf("mode = ");
    char str[10];
    getline(str, 6);
    pulse_mode = atoi(str);
    pc.printf("set\n");  
}

void anystep_set(){
    pc.printf("step count=");
    char str[10];
    getline(str, 6);
    anystep_cnt = atoi(str);
    pc.printf("steps\n");        
}

void pe_set(){
    char str[10];
    pc.printf("Pe width=");
    getline(str, 6);
    Pe_width = atoi(str);
    pc.printf(" us\n");
    pc.printf("Pe wait=");
    getline(str, 6);
    Pe_wait = atoi(str);
    pc.printf(" us\n");        
}

void spk_set(){
    char str[10];
    pc.printf("SPK period=");
    getline(str, 6);
    pwm_period = atof(str)/1000000;
    pwm2_period = pwm_period;
    pc.printf(" us\n");
    pc.printf("SPK ON=");
    getline(str, 6);
    pwm_duty = atof(str)/(pwm_period*1000000);
    pwm2_duty = pwm_duty;
    pc.printf(" us\n");        
}

void voltage_set(){
    char str[10];
    pc.printf("Voltage=");
    getline(str, 6);
    Vset = atof(str);
    Dac_out_process(Vset);
    pc.printf(" V\n");
}

void vref_set(){
    char str[10];
    pc.printf("Vref=");
    getline(str, 6);
    vref_value = atof(str)/3.3;
    pc.printf(" V\n");    
}

void pulse_train_set(){
    char str[12];
    pc.printf("Pulese(1)=");
    int n = pc.getc()-48;
    pc.putc(n+48);
    pc.printf(" "); 
    int m = 1;
    pc.printf(" ");    
    while(m<13){
        getline(str, 12);
        pattern[n][m]=strtol(str,NULL,2);//文字列を2進数として取り込み
        pc.printf(" ");
        m++;
    }
    pc.printf("\n");
}

void reduce_wait(){
    if(pulse_period>0){pulse_period--;}
    pc.printf("%dms" ,pulse_period);
}

void set_stopbit(){
    __disable_irq(); // 禁止
    wait(0.3);
    stop_bit=1;
}

void int_en(){
    int_act=0;
    __enable_irq(); // 許可 
}

void sequence_run(){
    int i=0;
    pc.printf("sequence");
    while(i<20){
        if(pseq[seq_number][i][2] ==0 && pseq[seq_number][i][3] ==0){break;}//M0M1step数がゼロだったらシーケンス終了
        rotate(pseq[seq_number][i][0],pseq[seq_number][i][1],
                pseq[seq_number][i][2],pseq[seq_number][i][3],
                pseq[seq_number][i][4],pseq[seq_number][i][5],
                pseq_vm[i][1]);
        i++;
        //pc.printf("%d",i);
    }
}
///////////////////////////////////////
//フォトインタラプタ検出関係/////////////
///////////////////////////////////////
void pipulse_copy(int pi_pulse_r){
    int import_num = 0;
    switch(pi_pulse_r){
        case 2:
        case 3:import_num = 2;break;
        case 4:
        case 5:import_num = 4;break;
    }
    for( int i = 0; i < 13; i++){//PI用のパルス設定をコピー
        pattern[7][i] = pattern[import_num][i];
        pwidth[7][i] = pwidth[import_num][i];
        pcnt[7][i] = pcnt[import_num][i];
        pattern[8][i] = pattern[import_num+1][i];
        pwidth[8][i] = pwidth[import_num+1][i];
        pcnt[8][i] = pcnt[import_num+1][i];        
        }
}

void pipulse_set(){
    pc.printf("PI Pulse set\n");
    pc.printf("Pulse_set(1)=");
    int pi_pulse_r = pc.getc()-48;
    pipulse_copy(pi_pulse_r);
    if(pi_pulse_r % 2 ==0){pi_pulse = 7; }
    else{pi_pulse = 8;}
    pc.printf(" %d(%d) select\n",pi_pulse_r,pi_pulse);

    pc.printf("PI period(Hz)=");
    char str[10];
    getline(str, 9);
    pi_period = (int)(1/atof(str)*1000000);
    pc.printf("Hz %dus\n",pi_period);  

    pc.printf("PI Voltage=");
    getline(str, 6);
    pi_vset = atof(str);
    pc.printf(" V\n");

    pc.printf("Step/round =");
    getline(str, 6);
    full_step = atoi(str);
    pc.printf(" steps\n");

    pc.printf("PI mode =");
    getline(str, 6);
    pi_mode = atoi(str);
    pc.printf(" \n");

    pc.printf("PI offset =");
    getline(str, 6);
    pi_offset = atoi(str);
    if(pi_pulse==8 && pi_offset != 0){//逆転パルスだったらoffset量変更
        pi_offset = full_step - pi_offset;
    }
    pc.printf(" steps\n");
    if(full_step<180){pi_judg=1;}//180step/周未満だったら、駆動中検出有効               
}

//パルス中検出したADCとの比較
int pi_comp(){
    int pi_adc = 0;
    pi_adc = 3300*piout;
    if(pi_adc < pi_inpulse && pi_judg ==1 ){//パルス中検出したADCの値と比較
        pi_adc = pi_inpulse;
        }
    return pi_adc ; 
}

//Photo 閾値電圧設定
void pivth_set(){
    pictl = 1;//PI LED ON 
    wait(0.05);
    int pi_adc[2000]={};//配列初期化 1周のステップ数以上にする
    int pi_min[]={3300,3300,3300};//
    int pi_max[]={0,0,0};//    

    int i = 0;
    //if (pi_mode ==3){//pi検出モード=1
    //    rotate(pi_pulse^0b1111,0,i+8,0,pi_period,0,pi_vset);//検出とは逆方法に6step移動
    //}
    if (pi_judg ==1){pi_detstep = 0;}
    else{pi_detstep = 1;}
    pi_inpulse = 0;
    while(i < full_step+1){
        //float piout_value = piout*3300;
        pi_adc[i] = pi_comp();
        if(pi_min[0]>pi_adc[i]){//PI出力の下位3位を抽出
            pi_min[2] = pi_min[1];
            pi_min[1] = pi_min[0];
            pi_min[0] = pi_adc[i];
        }
        else if(pi_min[1]>pi_adc[i]){//PI出力の下位3位を抽出
            pi_min[2] = pi_min[1];
            pi_min[1] = pi_adc[i];
        }
        else if(pi_min[2]>pi_adc[i]){//PI出力の下位3位を抽出
            pi_min[2] = pi_adc[i];
        }                
        if(pi_max[0]<pi_adc[i]){//PI出力の上位3位を抽出
            pi_max[2] = pi_max[1];
            pi_max[1] = pi_max[0];
            pi_max[0] = pi_adc[i];
        }
        else if(pi_max[1]<pi_adc[i]){//PI出力の上位3位を抽出
            pi_max[2] = pi_max[1];
            pi_max[1] = pi_adc[i];
        }
        else if(pi_max[2]<pi_adc[i]){//PI出力の上位3位を抽出
            pi_max[2] = pi_adc[i];
        }        
        rotate(pi_pulse,0,1,0,pi_period,0,pi_vset);
        pc.printf("%d mV\n",pi_adc[i]);//デバッグ用
        /*if (pi_mode ==3){//pi検出モード=1
            if((pi_max[pi_detstep]-pi_min[pi_detstep])>600){//PImax記録済み
                if(3300*piout<pi_min[pi_detstep]+200){//PI　lowの位置
                    rotate(pi_pulse^0b1111,0,i+10,0,pi_period,0,pi_vset);
                    break;
                }
            }
        }*/
        i++;
    }
    pivth = (int)pi_max[pi_detstep] * 0.8;//PI出力の上位2番目の0.8倍を閾値とする.
    if((pivth-pi_min[1]) > pivth * 0.2 && pivth > 600){//閾値設定をBest2に変更
        pc.printf("result OK\n");
    }
    else{pc.printf("result NG\n");}
    /*
    else{
        if(pi_max[pi_detstep] < 1500 && full_step < 180){//fullステップ180未満の場合で、Pimaxが1.5V以下だったら、
            if((pi_max[pi_detstep]-pi_min[pi_detstep])>300){//差分300mVでもOKとする
                pc.printf("result OK\n");
            }
            else{pc.printf("result NG\n");}
        }
        else{pc.printf("result NG\n");}
    }
    */
    pc.printf("pi_vth= %dmV\n",pivth);
    pc.printf("pi_max= %d/%d/%dmV\n",pi_max[0],pi_max[1],pi_max[2]);
    pc.printf("pi_min= %d/%d/%dmV\n",pi_min[0],pi_min[1],pi_min[2]);
    pictl = 0;//PI LED OFF
}
//Photo 初期位置検出
void piposi_set(){
    pictl = 1;//PI LED ON
    rotate(6,0,1,0,20000,0,pi_vset);//極性合わせ
    wait(0.05);
    int pierr = 0;
    int pi_adc = 0;
    //if(pivth==3300){pivth_set();}//pivthがセットされていなかったら
    int i = 0;
    while(3300*piout > pivth-100){//PI outがVthより小さくなるまで正転
        rotate(pi_pulse,0,1,0,pi_period,0,pi_vset);
        i++;
        if(i > full_step){
            pierr = 1;
            rotate(pi_pulse,0,10,0,pi_period,0,pi_vset);
            break;
        }
    }
    i = 0;
    while(pi_adc < pivth && pierr==0){//PI outがVthより大きくなるまで正転
        rotate(pi_pulse,0,1,0,pi_period,0,pi_vset);
        pi_adc = pi_comp();
        i++;
        if(i > full_step){
            pierr = 2;
            break;
        }
    }
    rotate(pi_pulse,0,pi_detstep,0,pi_period,0,pi_vset);//検出位置の1step奥をゼロ位置

    if(pierr==0){pc.printf(" %dmV result OK\n",pi_adc);}
    else {pc.printf(" result NG\n");;}
    M0_posi=0;//ここをM0の0位置とする
    pictl = 0;//PI LED OFF
    rotate(pi_pulse,0,pi_offset,0,pi_period,0,pi_vset);//offset分ずらす
}

//Photo step miss確認
void piposi_check(){
    int pierr = 0;
    int pierr_check = 3;                        //pi位置ズレステップを何ステップまでチェックするか
    int pierr_stepmiss = 5;                     //step miss 数チェックの際に±何ステップチェックするか              
    pierr_check = pierr_check + full_step/360;  //360step/周以上の場合、err_checkステップを増やす
    if(pi_mode == 2){
        pierr_check = pierr_check + pierr_stepmiss;
        rotate(6,0,1,0,20000,0,pi_vset);//極性合わせ
        }
    float piout_hold[2];
    pictl = 1;//PI LED ON
    wait(0.05);

    Goto_posi(pi_pulse,pierr_check,pi_period,pi_vset);//zero位置のpierr_check step前に移動
    piout_hold[0] = pi_comp(); 

    int i = pierr_check + pierr_stepmiss;
    int err_cnt = 0;
    if(pi_mode == 2){
        while(pi_comp() > pivth){//フォト検出がLowになるまで進める
            rotate(pi_pulse,0,1,0,pi_period,0,pi_vset);//1step移動
            i--;
            if(i < 0){pierr = 3;break;}            
        }
        while(pi_comp() < pivth && i > 0){//フォト検出がhiになるまで進める
            rotate(pi_pulse,0,1,0,pi_period,0,pi_vset);//1step移動
            i--;
            if(i < 0){pierr = 1;break;}             
        }
        if(pi_judg == 0){
            rotate(pi_pulse,0,pi_detstep,0,pi_period,0,pi_vset);//検出位置の1step奥がゼロ位置
        }
        if(M0_posi > full_step/2){err_cnt =  M0_posi-full_step;}
        else{err_cnt = M0_posi;}
        pc.printf(" Posi=%d ",err_cnt);
        if(M0_posi > pierr_stepmiss && M0_posi < full_step-pierr_stepmiss){pierr = 1;}
        M0_posi = 0;        
    }
    else{
        if(piout_hold[0] > pivth * 1){pierr = 3;}
        rotate(pi_pulse,0,pierr_check,0,pi_period,0,pi_vset);//zero位置に移動
    }

    piout_hold[1] = pi_comp(); 
    if(piout_hold[1] < pivth * 0.9){pierr=1;}
    if(piout_hold[1] < piout_hold[0]+100){pierr=1;}

    switch(pierr){
        case 0: if(pi_mode ==1 && pi_offset > full_step/2){
                    rotate(pi_pulse^0b1111,0,full_step-pi_offset+3,0,pi_period,0,pi_vset);
                    rotate(pi_pulse,0,3,0,pi_period,0,pi_vset);//バックラッシュ補正
                }
                else{
                    rotate(pi_pulse,0,pi_offset,0,pi_period,0,pi_vset);//offset分ずらす
                }
                pc.printf(" result OK\n");
                break;
        default:pc.printf(" result NG%d\n",pierr);
                if(pi_mode ==2){
                    rotate(pi_pulse^0b1111,0,60,0,pi_period,0,pi_vset);//逆極性ミスから位置セットする時間を短縮するための動作
                }
                break;        
    }
    pc.printf("-%dstep:%.0fmV\n",pierr_check,piout_hold[0]);//デバッグ用
    pc.printf(" 0step:%.0fmV\n",piout_hold[1]);//デバッグ用
    pictl = 0;//PI LED OFF
}

void pc_rx(){
    int command = pc.getc();
    //pc.putc(command);
    switch(command){
        case '0':M0_posi=0;
                M1_posi=0;
                pc.printf("Zero position set\n");
                break;
        case '1':pulse_set();
                //pc.printf("End!\n");
                break;
        case '2':pulse_period_set();
                //pc.printf("End!\n");            
                break;
        case '3':pulse_width_set();
                //pc.printf("End!\n");        
                break;
        case '4':pulse_num_set();
                //pc.printf("End!\n");
                break;
        case '5':sequence_set();
                pc.printf("End!\n");
                break;
        case '6':mode_set();
                //pc.printf("End!\n");
                break;
        case '7':anystep_set();
                //pc.printf("End!\n");
                break;
        case '8':pe_set();
                //pc.printf("End!\n");
                break;                                                                               
        case '9':sequence_run();
                pc.printf("End!\n");
                break;
        case '-':spk_set();
                break;
        case '^':voltage_set();
                break;
        case 'p':pulse_train_set();
                break;
        case 'o':vref_set();
                //pc.printf("End!\n");
                break;                                             
        case 'z':rotate(pulse_setnum,0,1,0,pulse_period,pulse_mode,Vset);
                pc.printf("End!\n");
                break;
        case 'x':rotate(pulse_setnum+1,0,1,0,pulse_period,pulse_mode,Vset);
                pc.printf("End!\n");
                break;
        case 'c':rotate(0,pulse_setnum,0,1,pulse_period,pulse_mode,Vset);
                pc.printf("End!\n");
                break;
        case 'v'://rotate(0,pulse_setnum+1,0,1,pulse_period,pulse_mode,Vset);
                //pc.printf("End!\n");
                pc.printf("%s\n",soft_rev);
                break;
        case 'b':rotate(pulse_setnum,0,anystep_cnt,0,pulse_period,pulse_mode,Vset);
                pc.printf("End!\n");
                break;
        case 'n':rotate(pulse_setnum+1,0,anystep_cnt,0,pulse_period,pulse_mode,Vset);
                pc.printf("End!\n");
                break;        
        case 'h':reduce_wait();
        case 'a':rotate(pulse_setnum,0,360,0,pulse_period,pulse_mode,Vset);
                pc.printf("End!\n");
                break;
        case 'j':reduce_wait();            
        case 's':rotate(pulse_setnum+1,0,360,0,pulse_period,pulse_mode,Vset);
                pc.printf("End!\n");
                break;
        case 'k':reduce_wait();        
        case 'd':rotate(0,pulse_setnum,0,360,pulse_period,pulse_mode,Vset);
                pc.printf("End!\n");
                break;
        case 'l':reduce_wait();        
        case 'f':rotate(0,pulse_setnum+1,0,360,pulse_period,pulse_mode,Vset);
                pc.printf("End!\n");
                break;
        case 'q'://rotate(pulse_setnum,pulse_setnum,360,360,pulse_period,pulse_mode);
                rotate(6,0,1,0,pulse_period,pulse_mode,Vset);
                pc.printf("End!\n");
                break;            
        case 'w'://rotate(pulse_setnum+1,pulse_setnum+1,360,360,pulse_period,pulse_mode,Vset);
                pivth_set();
                pc.printf("End!\n");
                break;
        case 'e'://rotate(pulse_setnum,pulse_setnum+1,360,360,pulse_period,pulse_mode,Vset);
                piposi_set();
                pc.printf("End!\n");
                break;
        case 'r'://rotate(pulse_setnum+1,pulse_setnum,360,360,pulse_period,pulse_mode,Vset);
                piposi_check();
                pc.printf("End!\n");
                break;
        case 't'://rotate(pulse_setnum,0,1860,0,pulse_period,pulse_mode,Vset);
                pipulse_set();
                pc.printf("End!\n");
                break;
        case 'y':rotate(pulse_setnum+1,0,1860,0,pulse_period,pulse_mode,Vset);
                pc.printf("End!\n");
                break;                      
        case 'm':Main_menu();
                break;
        default:break;
    }
}
/////////////////////////////////////////////////////////////////////////////
void led_cont(float st_duty,float en_duty, float step){
    float led_duty = st_duty;
    if(st_duty < en_duty){
        while (led_duty <= en_duty){
            pwm_led = led_duty;
            wait(0.010);
            led_duty = led_duty + step;
        }
    }
    else{
        while (led_duty >= en_duty){
            pwm_led = led_duty;
            wait(0.010);
            led_duty = led_duty - step;
        }        
    }
}
void moon_demo(){
    for  (int i = 0; i < 5; i++){
        led_cont(0,1,0.005);
        rotate(1,1,60,60,10000,0b011000001,Vset);
        led_cont(1,0,0.01);
        rotate(0,0,60,0,10000,0b001000001,Vset);
    }
}

void demo_event(){
    switch (seq_number){
    case 0:
    case 1:
        rotate(6,6,1,1,10000,0b000000001,Vset);//動作前に極性合わせ
        sequence_run();
        break;
    case 2:
        rotate(6,6,1,1,10000,0b000000001,Vset);//動作前に極性合わせ
        moon_demo();
        break;
    default:
        break;
    }
    mode_stat = 0;
    int_en();
    pc.printf("End!\n");
}

void seaquence_change(){
    seq_number = seq_number ++;
    if (seq_number > 2){seq_number=0;}
    for (int i = 0; i < seq_number+1; i++){
        LED = 1;
        wait(0.3);
        LED = 0;
        wait(0.3);
    }
    mode_stat = 0;
    int_en();
}

void button_event(){
    float press_time = button_time.read();//ボタン押し時間取得
    if (mybutton ==1){
        if (press_time < 2){
            wait(0.01);//チャタリング防止
            button_state = 0;//短押し確定
            mode_stat= 1;//シーケンス実行
        }
    }
    else{//mybutton == 0
        if (press_time >= 2){
            button_state = 0;//長押し確定
            mode_stat = 2;//シーケンス設定変更
        }
    }
    if (button_state == 0){
        button_time.stop();
    }
}

void but_fall(){
    __disable_irq(); // 禁止
    wait(0.01);//チャタリング防止
    if (mybutton == 0){
        if (button_state == 0){
            button_state = 1;
            button_time.reset();
            button_time.start();
        }
    }
}

int main()
{
#ifdef N446RE
    dac_vref = 1;
#endif
    pc.baud(921600);//115200//921600
    pc.attach(pc_rx,Serial::RxIrq);
    pc.printf("%s\n",soft_rev);//Teraterm上に表示
    pulse_time.start();//パルス開始からのタイマ
    //Main_menu();
    zero_out =  0; //出力なし
    pwm_led = 0;
    pwm_led.period(0.0001);

    Pw_adj(); 
    Adj_dac();//起動時に電源調整
#ifdef N446RE
    dac_vref = 0;
#endif
    //mybutton.rise(&flip); //mybotton 立ち上がり割り込み有効
    mybutton.fall(&but_fall); //mybotton 立ち上がり割り込み有効
    //top_but.rise(&set_stopbit);
    Dtvrs_1.mode(PullDown);
    Dtvrs_2.mode(PullDown);
    Dtvrs_3.mode(PullDown);
    Dtvrs_4.mode(PullDown);

    while(1) {
        switch (button_state){
            case 1:
                button_event();
                break;
            default:
                break;
        }

        switch (mode_stat){
            case 0://zero_out = 0; //出力なし
                Zero_posi(0,0,10000);
                break;
            case 1://短押し処理
                demo_event();
                break;
            case 2://長押し処理
                seaquence_change();
                break;               
        }
    int_en();
    }
}