
import struct
from . import core


class InvalidChError(Exception):
    pass

class InvalidModeError(Exception):
    pass


ad_range_flags = (
    ('0_1V', '0_2P5V', '0_5V', '0_10V', '1_5V', '0_2V', '0_1p25V'),
    ('', '', '', '', '', '', '', ''),
    ('', '', '', '', '', '', '', ''),
    ('', '', '', '', '', '', '', ''),
    ('', '', '', '', '', '', '', ''),
)

class pci3165_driver(core.interface_driver):
    bit_flags_in = (
        (
            ('B0', 'B1', 'B2', 'B3', 'B4', 'B5', 'B6', 'B7'), #+00h
            ('B8', 'B9', 'B10', 'B11', 'B12', 'B13', 'B14', 'B15'), #+01h
            ('', '', '', '', '', '', '', ''), #+02h
            ('', '', '', '', '', '', '', 'BUSY'), #+03h
            ('CA0', 'CA1', 'CA2', 'CA3', '', '', '', ''), #+04h
            ('SD0', 'SD1', 'SD2', '', '', '', '', ''), #+05h
            ('RG1', 'RG2', '', '', '', '', '', ''), #+06h
            ('', '', '', '', '', '', '', ''), #+07h
            ('TC00', 'TC01', 'TC02', 'TC03', 'TC04', 'TC05', 'TC06', 'TC07'), #+08h
            ('GATE', '', '', '', '', '', '', ''), #+09h
            ('TC10', 'TC11', 'TC12', 'TC13', 'TC14', 'TC15', 'TC16', 'TC17'), #+0Ah
            ('', '', '', '', '', '', '', ''), #+0Bh
            ('', '', '', '', '', '', '', ''), #+0Ch
            ('TMR', 'BSY', 'TRG', '', '', '', '', ''), #+0Dh
            ('TCN0', 'TCN1', 'TCN2', 'TCN3', 'TCN4', 'TCN5', 'TCN6', 'TCN7'), #+0Eh
            ('TMR', 'BSY', 'TRG', '', '', '', '', ''), #+0Fh
            ('EXTG', 'EINT', '', '', '', '', '', 'DITG'), #+10h
            ('', '', '', '', '', '', '', ''), #+11h
            ('', '', '', '', '', '', '', ''), #+12h
            ('', '', '', '', '', '', '', ''), #+13h
            ('', '', '', '', '', '', '', ''), #+14h
            ('', '', '', '', '', '', '', ''), #+15h
            ('', '', '', '', '', '', '', ''), #+16h
            ('BID0', 'BID1', 'BID2', 'BID3', 'M/S', 'CLKOEN', 'TRGOEN', ''), #+17h
            ('', '', '', '', '', '', 'SMD0', 'SMD1'), #+18h
            ('', '', '', '', '', '', '', ''), #+19h
            ('', '', '', '', '', '', '', ''), #+1Ah
            ('', '', '', '', '', '', '', ''), #+1Bh
            ('', '', '', '', '', '', '', ''), #+1Ch
            ('', '', '', '', '', '', '', ''), #+1Dh
            ('IN1', 'IN2', '', '', '', '', '', ''), #+1Eh
            ('', '', '', '', '', '', '', ''), #+1Fh
        ),
        (
            ('', '', '', '', '', '', '', ''), #+00h
            ('', '', '', '', '', '', '', ''), #+01h
            ('', '', '', '', '', '', '', ''), #+02h
            ('', '', '', '', '', '', '', ''), #+03h
        )
    )
    
    bit_flags_out = (
        (
            ('', '', '', '', '', '', '', ''), #+00h
            ('', '', '', '', '', '', '', ''), #+01h
            ('', '', '', '', '', '', '', ''), #+02h
            ('', '', '', '', '', '', '', ''), #+03h
            ('CA0', 'CA1', 'CA2', 'CA3', '', '', 'MA', 'MB'), #+04h
            ('SD0', 'SD1', 'SD2', '', '', '', '', ''), #+05h
            ('RG1', 'RG2', '', '', '', '', '', ''), #+06h
            ('', '', '', '', '', '', '', ''), #+07h
            ('', '', '', '', '', '', '', ''), #+08h
            ('GATE', '', '', '', '', '', '', ''), #+09h
            ('', '', '', '', '', '', '', ''), #+0Ah
            ('', '', '', '', '', '', '', ''), #+0Bh
            ('', '', '', '', '', '', '', ''), #+0Ch
            ('', '', '', '', '', '', '', ''), #+0Dh
            ('', '', '', '', '', '', '', ''), #+0Eh
            ('TMR', 'BSY', 'TRG', '', '', '', '', ''), #+0Fh
            ('EXTG', 'EINT', '', '', '', '', '', ''), #+10h
            ('', '', '', '', '', '', '', ''), #+11h
            ('', '', '', '', '', '', '', ''), #+12h
            ('', '', '', '', '', '', '', ''), #+13h
            ('', '', '', '', '', '', '', ''), #+14h
            ('', '', '', '', '', '', '', ''), #+15h
            ('', '', '', '', '', '', '', ''), #+16h
            ('', '', '', '', 'M/S', 'CLKOEN', 'TRGOEN', ''), #+17h
            ('', '', '', '', '', '', 'SMD0', 'SMD1'), #+18h
            ('', '', '', '', '', '', '', ''), #+19h
            ('', '', '', '', '', '', '', ''), #+1Ah
            ('', '', '', '', '', '', '', ''), #+1Bh
            ('', '', '', '', '', '', '', ''), #+1Ch
            ('', '', '', '', '', '', '', ''), #+1Dh
            ('OUT1', 'OUT2', '', '', '', '', '', ''), #+1Eh
            ('', '', '', '', '', '', ''), #+1Fh
        ),
        (
            ('', '', '', '', '', '', '', ''), #+00h
            ('U/D', 'INC', 'CS', '', '', '', '', ''), #+01h
            ('', '', '', '', '', '', '', ''), #+02h
            ('U/D', 'INC', 'CS', '', '', '', '', ''), #+03h
        )
    )
    
    
    def get_board_id(self):
        bar = 0
        offset = 0x17
        size = 1
        
        ret = self.read(bar, offset, size)
        bid = ret.to_hex()[1]

        return bid


    def initialize(self):
        pass


    def get_device_info(self):
        samplingd = core.bit2bytes('1000')
        samplingf = [('I/O', 'FIFO', 'MEM', 'BUSM', '', '', '', '')]
        sampling = core.flagged_bytes(samplingd, samplingf)
        
        info = {
            'board_type': 3165,
            'board_id': self.board_id,
            'sampling_mode': sampling,
            'resolution': 16,
            'ch_count_s': 16,
            'ch_count_d': 8,
            'range': 
            
        }
        return info

    def set_board_config(self):
        pass

    def get_board_config(self):
        pass

    def set_sampling_config(self):
        pass
    
    
    
    def _verify_mode(self, mode):
        mode_list = ['single', 'diff']
        if mode in mode_list: pass
        else:
            msg = 'Mode must be single or diff mode '
            msg += 'while {0} mode is given.'.format(mode)
        return


    
    def _verify_ch(self, ch='', mode=''):
        ch_limit_single = 64
        ch_limit_diff = 32


        if mode == 'single':
            if ch in ['ch{0}'.format(i) for i in range(1, ch_limit_single+1)]: pass
            else:
                msg = 'Ch must be in 1ch-{0}ch with {1} mode '.format(ch_limit_single, mode)
                msg += 'while {0}ch is given.'.format(ch)
                raise InvalidChError(msg)
            return
        
        if mode == 'diff':
            if ch in ['ch{0}'.format(i) for i in range(1,ch_limit_diff+1)]: pass
            else:
                msg = 'Ch must be in 1ch-{0}ch with {1} mode'.format(ch_limit_diff, mode)
                msg += 'while {0}ch is given.'.format(ch)
                raise InvalidChError(msg)
            return




    def _set_sampling_config(self, mode='single'):
        bar = 0
        offset = 0x05


        if mode == 'single': mode_ = ''
        elif mode == 'diff': mode_ = 'SD0'
        
        flags = mode_


        self.set_flag(bar, offset, flags)
        return




    def _ch2bit(self, ch=''):
        if ch == '': return b''
        else:
            ch = int(ch.replace('ch', ''))
            ch = bin(ch-1).replace('0b', '0'*(8-(len(bin(ch-1))-2)))
            bit_list = [int(ch[i]) for i in range(len(ch))]
            bit_list.reverse()
            return bit_list




    def _list2voltage(self, vol_list=[]):
        vol_range = 10
        res = 12
        res_int = 2**12
        
        bytes_v = int.from_bytes(core.list2bytes(vol_list), 'little')
        vol = -vol_range + (vol_range/(res_int/2))*bytes_v


        return vol




    def _start_sampling(self, data):
        bar = 0
        offset = 0x04
        size = 1
        
        num = len(data)
        new_d = core.list2bytes(data)
        self.write(bar, offset, new_d)
        self._busy()
        return




    def _busy(self):
        bar = 0
        size = 1
        offset = 0x03


        busy = self.read(bar, offset, size)
        while busy.to_list()[7]==0:
            busy = self.read(bar, offset, size)
        return


    
    def set_sampling_config(self, singlediff=''):
        self._verify_mode(mode=singlediff)
        self._set_sampling_config(mode=singlediff)
        return


    
    def get_sampling_config(self):
        bar = 0
        offset = 0x05
        size = 1


        return self.read(bar, offset, size).print()




    def input_ad(self, ch='', singlediff='diff'):
        bar = 0
        size = 2
        offset = 0x00


        self._verify_mode(mode=singlediff)
        self._verify_ch(ch=ch, mode=singlediff)
        self._set_sampling_config(mode=singlediff)
        ch = self._ch2bit(ch)
        self._start_sampling(ch)


        ret = self.read(bar, offset, size)
        ret = self._list2voltage(ret.to_list())


        return ret


    
    def input_ad_master(self, singlediff='diff'): # for Mr.Inaba
        self._verify_mode(singlediff)
        mode = singlediff


        if mode == 'single': ch = 'ch1-ch64'
        elif mode == 'diff': ch = 'ch1-ch32'
        
        ch_ = ch.replace('ch', '').split('-')
        ch_initial, ch_final = int(ch_[0]), int(ch_[1])
        ch = [self.input_ad('ch{0}'.format(i)) for i in range(ch_initial, ch_final+1)]
        
        return ch


# History
# -------
# written by K.Sakasai
